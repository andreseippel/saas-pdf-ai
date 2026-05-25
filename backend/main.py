from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import fitz
import os
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from groq import Groq

# =========================
# CONFIG
# =========================

import os

GROQ_API_KEY = os.getenv("VUUurQyfdiSHxBLMbYooWGdyb3FYGdZQm14xhQ3vDkZJJv01jx5o")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

db = {}

# =========================
# MODELS
# =========================

class ChatRequest(BaseModel):
    filename: str
    question: str

# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {"status": "PDF AI ONLINE 🚀"}

# =========================
# UPLOAD
# =========================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    try:

        path = f"{UPLOAD_DIR}/{file.filename}"

        with open(path, "wb") as f:
            f.write(await file.read())

        doc = fitz.open(path)

        texts = []

        for page in doc:

            text = page.get_text()

            if text.strip():
                texts.append(text)

        embeddings = model.encode(texts)

        embeddings = np.array(
            embeddings
        ).astype("float32")

        index = faiss.IndexFlatL2(
            embeddings.shape[1]
        )

        index.add(embeddings)

        db[file.filename] = {
            "texts": texts,
            "index": index
        }

        return {
            "message": "PDF processado",
            "filename": file.filename
        }

    except Exception as e:
        return {
            "error": str(e)
        }

# =========================
# CHAT
# =========================

@app.post("/chat")
def chat(data: ChatRequest):

    try:

        if data.filename not in db:
            return {
                "error": "PDF não encontrado"
            }

        pdf_data = db[data.filename]

        query_embedding = model.encode(
            [data.question]
        )

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        D, I = pdf_data["index"].search(
            query_embedding,
            k=3
        )

        context = "\n\n".join([
            pdf_data["texts"][i]
            for i in I[0]
        ])

        prompt = f"""
Responda usando apenas o contexto abaixo.

CONTEXTO:
{context}

PERGUNTA:
{data.question}

RESPOSTA:
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = completion.choices[0].message.content

        return {
            "answer": answer
        }

    except Exception as e:
        return {
            "error": str(e)
        }