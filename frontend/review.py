import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="OrderBridge - Review", page_icon="📖", layout="centered")

st.title("📖 Order Review")
st.caption("Review your restaurant conversation and learn practical English phrases")

# ---------- Session ID input ----------

session_id = st.number_input("Enter Session ID", min_value=1, step=1, value=1)

if st.button("View Review"):
    with st.spinner("Loading..."):
        try:
            resp = requests.get(f"{API_BASE}/sessions/{session_id}/review")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure uvicorn is running at http://localhost:8000")
            st.stop()

    if resp.status_code == 404:
        st.error("Session not found. Please check the ID.")
        st.stop()
    elif resp.status_code != 200:
        st.error(f"Request failed: {resp.status_code}")
        st.stop()

    data = resp.json()
    session_info = data["session_info"]
    turns = data["turns"]
    summary = data["learning_summary"]

    # ---------- Session info ----------

    st.markdown("---")
    st.subheader("📋 Session Info")

    col1, col2, col3 = st.columns(3)
    col1.metric("Restaurant", session_info["restaurant_name"] or "N/A")
    col2.metric("Language", session_info["user_language"].upper())
    col3.metric("Status", "Completed ✅" if session_info["status"] == "completed" else "In Progress 🔄")

    created = session_info["created_at"][:16].replace("T", " ")
    st.caption(f"Started at: {created}")

    # ---------- Conversation replay ----------

    st.markdown("---")
    st.subheader("💬 Conversation Replay")

    if not turns:
        st.info("No conversation turns recorded for this session.")
    else:
        for turn in turns:
            speaker = turn["speaker"]
            text = turn["original_text"]
            translation = turn.get("translated_text")
            selected = turn.get("selected_response") or turn.get("final_response_text")

            if speaker == "server":
                st.markdown("🧑‍💼 **Server**")
                st.markdown(f"> {text}")
                if translation:
                    st.caption(f"💡 {translation}")
                st.markdown("")

            elif speaker == "user":
                st.markdown("🙋 **You**")
                st.markdown(f"> {selected or text}")
                st.markdown("")

            else:
                st.markdown("🤖 **System**")
                st.markdown(f"> {text}")
                st.markdown("")

    # ---------- Learning summary ----------

    st.markdown("---")
    st.subheader("🎓 What You Learned Today")

    col_a, col_b = st.columns(2)
    col_a.metric("Total Turns", summary["total_turns"])
    col_b.metric("Server Questions", summary["server_turns"])

    key_expressions = summary["key_expressions"]

    if not key_expressions:
        st.info("No key expressions recorded.")
    else:
        for expr in key_expressions:
            st.markdown("---")
            st.markdown(f"**🗣 Original:** {expr['original']}")
            st.markdown(f"**💬 Explanation:** {expr['translation']}")

            if expr["suggested_responses"]:
                st.markdown("**✅ Common Responses:**")
                cols = st.columns(len(expr["suggested_responses"]))
                for i, response in enumerate(expr["suggested_responses"]):
                    cols[i].button(response, key=f"btn_{expr['intent']}_{i}", disabled=True)
