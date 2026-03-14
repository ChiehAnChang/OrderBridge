import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Visual-Voice Connect - Review", page_icon="📖", layout="centered")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("frontend/style.css")

st.title("📖 Daily Review")
st.markdown("Listen and practice phrases from today's orders.")

# ---------- Session ID input ----------
# Use columns for a more mobile-friendly clean layout
col1, col2 = st.columns([3, 1])
with col1:
    session_id = st.number_input("Session ID", min_value=1, step=1, value=1, label_visibility="collapsed")
with col2:
    load_btn = st.button("Load")

if load_btn:
    with st.spinner("Loading..."):
        try:
            resp = requests.get(f"{API_BASE}/sessions/{session_id}/review")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend.")
            st.stop()

    if resp.status_code == 404:
        st.warning("No records found for this Session ID. Showing mock visual review data...")
        # Since backend might be mocked, mock the review payload for now
        data = {
            "session_info": {"restaurant_name": "Mock Restaurant"},
            "learning_summary": {
                "key_expressions": [
                    {
                        "original": "Wait a moment", 
                        "translation": "Wait 5 minutes", 
                        "icon": "⏳", 
                        "audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav" 
                    },
                    {
                        "original": "Chicken Curry", 
                        "translation": "Chicken Curry", 
                        "icon": "🍛", 
                        "audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars3.wav"
                    }
                ]
            }
        }
    elif resp.status_code != 200:
        st.error(f"Request failed: {resp.status_code}")
        st.stop()
    else:
        data = resp.json()

    # ---------- Learning summary ----------
    summary = data.get("learning_summary", {})
    key_expressions = summary.get("key_expressions", [])

    if not key_expressions:
        st.info("No practice items today.")
    else:
        st.markdown("### Tap to Practice")
        for idx, expr in enumerate(key_expressions):
            st.markdown('<div class="food-card">', unsafe_allow_html=True)
            
            icon = expr.get("icon", "📝")
            original = expr.get("original", "")
            
            # Using columns for visual arrangement
            scol1, scol2 = st.columns([1, 4])
            with scol1:
                st.markdown(f'<div style="font-size:50px;">{icon}</div>', unsafe_allow_html=True)
            with scol2:
                st.markdown(f'<div class="food-title" style="text-align: left; font-size: 24px;">{original}</div>', unsafe_allow_html=True)
            
            # Action button for playback
            audio_url = expr.get("audio_url")
            if audio_url:
                # In Streamlit, native st.audio renders an HTML5 audio control
                st.audio(audio_url)
            else:
                st.button("🔊 Play", key=f"play_{idx}")
                
            st.markdown('</div>', unsafe_allow_html=True)
