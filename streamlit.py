import streamlit as st
import random
import requests
import time
import uuid
import os

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")


# Streamed response emulator
def response_generator(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)


st.title("SK Insurance Claim Assistant")

# Sidebar for document management
with st.sidebar:
    st.header("Document Management")
    
    # Fetch and display sources
    try:
        sources_resp = requests.get(f"{FASTAPI_URL}/sources", timeout=10)
        if sources_resp.status_code == 200:
            sources = sources_resp.json()
            
            st.subheader("Indexed Documents")
            for source in sources:
                with st.expander(f"{source['filename']}"):
                    st.write(f"**Chunks:** {source['chunk_count']}")
                    if st.button(f"Delete", key=f"del_{source['doc_id']}"):
                        delete_resp = requests.delete(
                            f"{FASTAPI_URL}/sources/{source['doc_id']}",
                            timeout=10
                        )
                        if delete_resp.status_code == 200:
                            st.success(f"Deleted {source['filename']}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to delete")
            
            if st.button("🔄 Refresh Sources"):
                st.rerun()
        else:
            st.error("Failed to load sources")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.divider()
    
    # Ingestion section
    st.subheader("Ingest Documents")
    if st.button("Start Ingestion"):
        with st.spinner("Ingesting documents..."):
            ingest_resp = requests.post(
                f"{FASTAPI_URL}/ingest",
                json={},
                timeout=10
            )
            if ingest_resp.status_code == 200:
                job_data = ingest_resp.json()
                st.session_state.ingest_job_id = job_data["job_id"]
                st.success(f"Ingestion started! Job ID: {job_data['job_id']}")
            else:
                st.error("Failed to start ingestion")
    
    # Show ingestion status if available
    if "ingest_job_id" in st.session_state:
        st.subheader("Ingestion Status")
        status_resp = requests.get(
            f"{FASTAPI_URL}/ingest/status/{st.session_state.ingest_job_id}",
            timeout=10
        )
        if status_resp.status_code == 200:
            status = status_resp.json()
            st.write(f"**Status:** {status['status']}")
            if status.get('chunks_ingested'):
                st.write(f"**Chunks:** {status['chunks_ingested']}")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display sources if available
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# Accept user input
if user_input := st.chat_input("What is your insurance query?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{FASTAPI_URL}/chat",
                json={
                    "message": user_input,
                    "session_id": st.session_state.session_id,
                },
                timeout=60,
            )
            
            if resp.status_code == 200:
                data = resp.json()
                response_text = data["response"]
                # Note: To get sources, we'd need to modify the chat endpoint
                # to return sources. For now, we'll just show the response.
                sources = []
            else:
                response_text = "Error in the request"
                sources = []
        
        response = st.write_stream(response_generator(response_text))
        
        # Display sources if available
        if sources:
            with st.expander("📚 Sources"):
                for source in sources:
                    st.write(f"- {source}")
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "sources": sources
    })
