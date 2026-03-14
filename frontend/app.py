import streamlit as st
import requests
import os

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Visual-Voice Connect", page_icon="📱", layout="centered")

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("frontend/style.css")
except FileNotFoundError:
    pass

st.title("📱 Visual-Voice Connect")

# ---------- Session State Init ----------
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "input_method" not in st.session_state:
    st.session_state.input_method = None

# ---------- Session Bar ----------
with st.container():
    col_status, col_start, col_end = st.columns([3, 1, 1])

    with col_status:
        if st.session_state.session_id:
            st.success(f"Session #{st.session_state.session_id} active")
        else:
            st.info("No active session")

    with col_start:
        if st.button("▶ Start", use_container_width=True, disabled=st.session_state.session_id is not None):
            try:
                resp = requests.post(f"{API_BASE}/sessions/create", json={"user_language": "zh"})
                if resp.status_code == 200:
                    st.session_state.session_id = resp.json()["session_id"]
                    st.rerun()
                else:
                    st.error("Failed to start session.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend.")

    with col_end:
        if st.button("⏹ End", use_container_width=True, disabled=st.session_state.session_id is None):
            try:
                requests.post(f"{API_BASE}/sessions/{st.session_state.session_id}/complete")
            except requests.exceptions.ConnectionError:
                pass
            st.session_state.session_id = None
            st.rerun()

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📸 Scan Menu", "🎙️ Staff Audio Feedback", "📖 Daily Review"])

with tab1:
    st.header("")
    st.markdown('<div class="guide-arrow">🔽</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🙋 ➡️ 📸", help="Take a photo", use_container_width=True):
            st.session_state.input_method = "camera"
    with col2:
        if st.button("🙋 ➡️ 📤🖼️", help="Upload a photo", use_container_width=True):
            st.session_state.input_method = "upload"

    img_file = None
    if st.session_state.input_method == "camera":
        img_file = st.camera_input("📷", label_visibility="collapsed")
    elif st.session_state.input_method == "upload":
        img_file = st.file_uploader("🖼️", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if img_file is not None:
        st.image(img_file, caption="Captured Menu", use_container_width=True)
        if st.button("Process Menu"):
            with st.spinner("Processing..."):
                try:
                    files = {"file": ("menu.jpg", img_file.getvalue(), "image/jpeg")}
                    resp = requests.post(f"{API_BASE}/ocr", files=files)

                    if resp.status_code == 200:
                        data = resp.json()
                        items = data.get("items", [])
                        flags = data.get("cultural_flags", [])

                        if flags:
                            for flag in flags:
                                st.markdown(f'<div class="warning-flag">⚠️ Warning: {flag} detected</div>', unsafe_allow_html=True)

                        if not items:
                            st.info("No food items found. Please try again.")
                        else:
                            for item in items:
                                st.markdown('<div class="food-card">', unsafe_allow_html=True)
                                st.markdown(f'<div class="food-title">{item["name"]}</div>', unsafe_allow_html=True)
                                if "image_url" in item and item["image_url"]:
                                    st.image(item["image_url"], use_container_width=True)
                                if "audio_url" in item and item["audio_url"]:
                                    st.audio(item["audio_url"])
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("OCR endpoint is not ready yet. Generating mock visual cards...")
                        mock_items = [
                            {"name": "Chicken Curry", "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&q=80"},
                            {"name": "Rice", "image_url": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=500&q=80"}
                        ]
                        for item in mock_items:
                            st.markdown('<div class="food-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="food-title">{item["name"]}</div>', unsafe_allow_html=True)
                            st.image(item["image_url"], use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")

with tab2:
    st.header("")
    st.markdown('<div class="guide-arrow">🔽</div>', unsafe_allow_html=True)
    audio_val = st.audio_input("", label_visibility="collapsed")

    if audio_val is not None:
        st.audio(audio_val, format="audio/wav")
        if st.button("Translate to Icons"):
            with st.spinner("Translating..."):
                try:
                    files = {"file": ("audio.wav", audio_val.getvalue(), "audio/wav")}
                    resp = requests.post(f"{API_BASE}/stt", files=files)

                    if resp.status_code == 200:
                        data = resp.json()
                        intent_icon = data.get("icon", "❓")
                        intent_text = data.get("intent", "Unknown")
                        transcript = data.get("transcript", "")

                        st.markdown(f'<div class="intent-icon">{intent_icon}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="intent-text">{intent_text}</div>', unsafe_allow_html=True)

                        # Auto-save turn to session
                        if st.session_state.session_id:
                            requests.post(f"{API_BASE}/turns/add", json={
                                "session_id": st.session_state.session_id,
                                "speaker": "server",
                                "original_text": transcript,
                                "intent": intent_text,
                            })
                    else:
                        st.warning("STT endpoint is not ready yet. Serving mock icon response...")
                        st.markdown('<div class="intent-icon">⏳</div>', unsafe_allow_html=True)
                        st.markdown('<div class="intent-text">Wait 5 minutes</div>', unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")

with tab3:
    st.markdown("Listen and practice phrases from today's orders.")

    sid = st.session_state.session_id
    if sid:
        st.info(f"Showing review for Session #{sid}")
        load_btn = st.button("Load Review")
        session_id_to_load = sid
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            session_id_to_load = st.number_input("Session ID", min_value=1, step=1, value=1, label_visibility="collapsed")
        with col2:
            load_btn = st.button("Load")

    if load_btn:
        with st.spinner("Loading..."):
            try:
                resp = requests.get(f"{API_BASE}/sessions/{session_id_to_load}/review")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend.")
                st.stop()

        if resp.status_code == 404:
            st.warning("No records found. Showing mock data...")
            data = {
                "learning_summary": {
                    "key_expressions": [
                        {"original": "Wait a moment", "translation": "Wait 5 minutes", "icon": "⏳"},
                        {"original": "Chicken Curry", "translation": "Chicken Curry", "icon": "🍛"},
                    ]
                }
            }
        elif resp.status_code != 200:
            st.error(f"Request failed: {resp.status_code}")
            st.stop()
        else:
            data = resp.json()

        key_expressions = data.get("learning_summary", {}).get("key_expressions", [])

        if not key_expressions:
            st.info("No practice items today.")
        else:
            st.markdown("### Tap to Practice")
            for idx, expr in enumerate(key_expressions):
                st.markdown('<div class="food-card">', unsafe_allow_html=True)
                scol1, scol2 = st.columns([1, 4])
                with scol1:
                    st.markdown(f'<div style="font-size:50px;">{expr.get("icon", "📝")}</div>', unsafe_allow_html=True)
                with scol2:
                    st.markdown(f'<div class="food-title" style="text-align:left;font-size:24px;">{expr.get("original", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#888;">{expr.get("translation", "")}</div>', unsafe_allow_html=True)
                audio_url = expr.get("audio_url")
                if audio_url:
                    st.audio(audio_url)
                st.markdown('</div>', unsafe_allow_html=True)
