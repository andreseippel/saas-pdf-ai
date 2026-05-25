import streamlit as st
import requests
import os

# ========================
# API URL
# ========================

API_URL = os.getenv(
    "API_URL",
    "https://bubbz-pdf-ai.onrender.com"
)

# ========================
# PAGE
# ========================

st.set_page_config(
    page_title="Bubbz AI",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Bubbz AI")
st.caption("Chat with your PDF using AI")

# ========================
# SESSION
# ========================

if "filename" not in st.session_state:
    st.session_state.filename = None

# ========================
# PDF UPLOAD
# ========================

st.header("1. Upload PDF")

file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if file:

    with st.spinner("Processing PDF..."):

        try:

            res = requests.post(
                f"{API_URL}/upload",
                files={
                    "file": (
                        file.name,
                        file.getvalue(),
                        "application/pdf"
                    )
                }
            )

            data = res.json()

            if "error" in data:
                st.error(data["error"])

            else:
                st.success("PDF uploaded successfully 🚀")
                st.session_state.filename = data["filename"]

        except Exception as e:
            st.error(f"Connection error: {str(e)}")

# ========================
# CHAT
# ========================

if st.session_state.filename:

    st.header("2. Chat with PDF")

    question = st.text_input(
        "Ask a question:"
    )

    if question:

        with st.spinner("Generating answer..."):

            try:

                res = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "filename": st.session_state.filename,
                        "question": question
                    }
                )

                data = res.json()

                if "error" in data:
                    st.error(data["error"])

                else:
                    st.subheader("Answer")
                    st.write(data["answer"])

            except Exception as e:
                st.error(f"Connection error: {str(e)}")

else:
    st.info("Upload a PDF to start chatting.")