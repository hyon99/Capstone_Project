import streamlit as st
import uuid

from physics_study_buddy import run_graph


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Physics AI Assistant",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS (WEBSITE LOOK)
# -----------------------------
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: 700;
    color: #2c3e50;
}
.sub-title {
    font-size: 18px;
    color: #7f8c8d;
}
.block {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8f9fa;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# SESSION STATE
# -----------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "debug" not in st.session_state:
    st.session_state.debug = False


# -----------------------------
# HELPERS
# -----------------------------
def trim_messages(msgs, k=4):
    return msgs[-k:] if msgs else []


def safe_run(question):
    try:
        msgs = trim_messages(st.session_state.messages)

        result = run_graph(
            question=question,
            thread_id=st.session_state.thread_id,
            messages=msgs
        )

        result["messages"] = trim_messages(result.get("messages", []))
        return result

    except Exception as e:
        return {
            "answer": f"⚠️ Error: {str(e)[:120]}",
            "route": "error",
            "faithfulness": 0.0,
            "messages": st.session_state.messages
        }


# -----------------------------
# HEADER (WEBSITE STYLE)
# -----------------------------
st.markdown('<div class="main-title">⚡ Physics AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">RAG + Tools + Memory Powered Learning System</div>', unsafe_allow_html=True)

st.markdown("---")


# -----------------------------
# LAYOUT (2 COLUMNS)
# -----------------------------
left_col, right_col = st.columns([2, 1])


# =============================
# LEFT SIDE → CHAT AREA
# =============================
with left_col:

    st.markdown("### 💬 Chat Interface")

    chat_container = st.container()

    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f"**🧑 You:** {chat['content']}")
            else:
                st.markdown(f"**🤖 Assistant:** {chat['content']}")

    user_input = st.text_input("Ask a physics question...")

    if st.button("Send") and user_input:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking..."):
            result = safe_run(user_input)

        answer = result["answer"]

        st.session_state.messages = result["messages"]

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()


# =============================
# RIGHT SIDE → CONTROL PANEL
# =============================
with right_col:

    st.markdown("### ⚙️ Control Panel")

    st.markdown('<div class="block">', unsafe_allow_html=True)

    if st.button("🆕 New Chat"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.success("New session started")

    st.session_state.debug = st.checkbox("Enable Debug Mode")

    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # SYSTEM INFO
    # -------------------------
    st.markdown("### 📊 System Info")

    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.write("Model: LLaMA (Groq)")
    st.write("RAG: ChromaDB")
    st.write("Memory: Enabled (trimmed)")
    st.write(f"Thread ID: {st.session_state.thread_id[:8]}...")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # DEBUG PANEL
    # -------------------------
    if st.session_state.debug and st.session_state.chat_history:

        st.markdown("### 🧪 Debug Info")

        last_response = st.session_state.chat_history[-1]

        st.markdown('<div class="block">', unsafe_allow_html=True)

        st.write("Route:", result.get("route", "N/A") if 'result' in locals() else "N/A")
        st.write("Faithfulness:", round(result.get("faithfulness", 0), 3) if 'result' in locals() else "N/A")

        if 'result' in locals() and result.get("tool_result"):
            st.write("Tool Output:", str(result["tool_result"])[:200])

        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Capstone Project")