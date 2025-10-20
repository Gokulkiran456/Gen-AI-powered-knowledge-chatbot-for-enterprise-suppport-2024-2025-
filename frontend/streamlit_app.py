import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Enterprise GenAI Chatbot", page_icon="🤖")
st.title("🤖 Enterprise Knowledge Assistant")

with st.sidebar:
    st.header("Settings")
    backend = st.text_input("Backend URL", value=BACKEND_URL, help="FastAPI base URL")
    st.write("Ingest docs from ./data/docs via backend:")
    if st.button("Ingest now"):
        r = requests.post(f"{backend}/api/ingest", json={})
        st.success(r.json())

if "history" not in st.session_state:
    st.session_state.history = []

q = st.chat_input("Ask a question about your company's policies, IT, etc...")
if q:
    st.session_state.history.append({"role": "user", "content": q})
    with st.spinner("Thinking..."):
        r = requests.post(f"{backend}/api/ask", json={"question": q}, timeout=120)
        payload = r.json()
        ans = payload.get("answer", "")
        srcs = payload.get("sources", [])
    st.session_state.history.append({"role": "assistant", "content": ans, "sources": srcs})

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(sorted(set(msg["sources"]))))
