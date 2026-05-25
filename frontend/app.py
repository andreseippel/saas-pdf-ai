import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("📄 Bubbz - PDF AI Chat")

# =========================
# SESSION
# =========================

if "filename" not in st.session_state:
    st.session_state.filename = None

# =========================
# UPLOAD
# =========================

st.header("1. Upload PDF")

file = st.file_uploader(
    "Envie um PDF",
    type=["pdf"]
)

if file is not None:

    with st.spinner("Processando PDF..."):

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

    if "filename" in data:

        st.session_state.filename = data["filename"]

        st.success("PDF processado 🚀")

    else:

        st.error(
            data.get("error")
        )

# =========================
# CHAT
# =========================

st.header("2. Pergunte ao PDF")

if st.session_state.filename:

    question = st.text_input(
        "Digite sua pergunta"
    )

    if question:

        with st.spinner("Pensando..."):

            res = requests.post(
                f"{API_URL}/chat",
                json={
                    "filename":
                    st.session_state.filename,

                    "question":
                    question
                }
            )

        data = res.json()

        if "answer" in data:

            st.subheader("Resposta")

            st.write(data["answer"])

        else:

            st.error(
                data.get("error")
            )

else:

    st.info(
        "Faça upload de um PDF primeiro"
    )