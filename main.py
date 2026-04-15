# OpenCortex - main.py

# Required Libraries
import streamlit as st

# Page Configuration
st.set_page_config(page_title="OpenCortex", layout="wide")

# Sidebar for Data Sources
with st.sidebar:
    st.header("Data Sources")
    st.markdown("Add different data sources to the local brain")

    # Upload files with different modalities
    uploaded_files = st.file_uploader("Upload Documents or Images",
                                      accept_multiple_files = True,
                                      type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'odt'])
    
    # Check files and output the number of uploaded files
    if uploaded_files:
        st.success(f"{len(uploaded_files)} files ready for indexing.")

        # Button for triggering the RAG pipeline
        if st.button("Sync to OpenCortex"):
            st.info("Preparing to index data sources...")


# Main Interface
st.title ("OpenCortex")
st.caption("Intelligence, but Open, Private and Local")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Input and Logic Loop
if prompt := st.chat_input("Ask OpenCortex..."):

    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Placeholder for AI Response
    with st.chat_message("assistant"):
        response = "Interface ready. Next, we connect my 'neurons' (Ollama)!"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

