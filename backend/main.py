from fastapi import FastAPI, UploadFile, File
from groq import Groq
import fitz
import os

app = FastAPI()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# GROQ
client = Groq(
    api_key=os.getenv("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")
)

# simple memory db
db = {}

@app.get("/")
def home():
    return {"status": "Bubbz AI ONLINE 🚀"}

# ========================
# PDF UPLOAD
# ========================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    try:
        path = f"{UPLOAD_DIR}/{file.filename}"

        with open(path, "wb") as f:
            f.write(await file.read())

        doc = fitz.open(path)

        full_text = ""

        for page in doc:
            page_text = page.get_text()

            if page_text:
                full_text += page_text + "\n"

        if not full_text.strip():
            return {"error": "PDF contains no readable text"}

        db[file.filename] = full_text

        return {
            "message": "PDF uploaded successfully 🚀",
            "filename": file.filename
        }

    except Exception as e:
        return {"error": str(e)}

# ========================
# CHAT
# ========================
@app.post("/chat")
def chat(data: dict):

    try:
        filename = data.get("filename")
        question = data.get("question")

        if filename not in db:
            return {"error": "PDF not found"}

        context = db[filename][:12000]

        prompt = f"""
You are an AI assistant that answers questions
using only the uploaded PDF content.

PDF Content:
{context}

Question:
{question}

If the answer is not in the document,
reply exactly with:
"Not found in document."
"""

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = completion.choices[0].message.content

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}