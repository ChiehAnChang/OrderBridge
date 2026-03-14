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

# Tabs for easy navigation
tab1, tab2 = st.tabs(["📸 Scan Menu", "🎙️ Staff Audio Feedback"])

with tab1:
    st.header("📸")
    
    st.markdown('<div class="guide-arrow">🔽</div>', unsafe_allow_html=True)
    
    # Track the active input method in session state
    if "input_method" not in st.session_state:
        st.session_state.input_method = None

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
                                # Audio playback
                                if "audio_url" in item and item["audio_url"]:
                                    st.audio(item["audio_url"])
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("OCR endpoint is not ready yet. Generating mock visual cards...")
                        # Mock data for frontend demo purposes
                        mock_items = [
                            {"name": "Chicken Curry", "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&q=80"},
                            {"name": "Rice", "image_url": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=500&q=80"}
                        ]
                        for item in mock_items:
                            st.markdown(f'<div class="food-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="food-title">{item["name"]}</div>', unsafe_allow_html=True)
                            st.image(item["image_url"], use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")

with tab2:
    st.header("🎙️")
    
    st.markdown('<div class="guide-arrow">🔽</div>', unsafe_allow_html=True)
    audio_val = st.audio_input("🎙️", label_visibility="collapsed")
    
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
                        
                        st.markdown(f'<div class="intent-icon">{intent_icon}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="intent-text">{intent_text}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("STT endpoint is not ready yet. Serving mock icon response...")
                        st.markdown('<div class="intent-icon">⏳</div>', unsafe_allow_html=True)
                        st.markdown('<div class="intent-text">Wait 5 minutes</div>', unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")
