# app.py
import streamlit as st
import src.core as core
from utils.logger import setup_logger

logger = setup_logger("app_ui")
st.set_page_config(page_title="OpenCortex", layout="wide")

if not core.check_ollama():
    st.error("OpenCortex cannot find the AI service. Please check your installation.")
    st.stop()

st.title("OpenCortex")
st.caption("Intelligence, but Open, Private and Local (Powered by ChromaDB)")

with st.sidebar:
    st.header("Data Sources")
    uploaded_files = st.file_uploader(
        "Upload Documents",
        accept_multiple_files=True,
        type=['txt', 'pdf']
    )
    
    if uploaded_files:
        if st.button("Sync to OpenCortex"):
            with st.spinner("Embedding documents with Nomic into ChromaDB..."):
                success = core.process_uploaded_files(uploaded_files)
                if success:
                    st.success("Brain updated and saved to Vector Database!")
                else:
                    st.error("Could not extract text from files.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask OpenCortex..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We don't need to pass the giant context string anymore! 
        # core.py handles the database retrieval internally now.
        full_response = st.write_stream(
            core.opencortex_response_stream("llama3.2", prompt)
        )

    st.session_state.messages.append({"role": "assistant", "content": full_response})