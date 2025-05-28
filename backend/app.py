from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from dotenv import load_dotenv
from chat_engine import get_conversation_chain
from pdf_manager import save_pdf, delete_pdf, list_pdfs
from auth import authenticate_admin, create_access_token, get_current_admin
from pydantic import BaseModel
from openai import OpenAI
from load_and_embed import delete_pdf_vectors, embed_single_pdf
import shutil

# Tambahkan variabel global untuk progress embedding
embedding_progress = {"progress": 0, "status": "idle"}

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS agar frontend React bisa akses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # sesuaikan dengan alamat frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=openai_api_key)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation = get_conversation_chain(openai_api_key)
    response = conversation({"question": request.question})
    answer = response["chat_history"][-1].content
    return {"answer": answer}

# Endpoint login admin
@app.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...)):
    if not authenticate_admin(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(username)
    return {"access_token": token, "token_type": "bearer"}

# Endpoint upload PDF (hanya admin)
@app.post("/admin/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_admin: str = Depends(get_current_admin)
):
    save_pdf(file)
    return {"detail": "PDF uploaded successfully"}

# Endpoint hapus PDF (hanya admin)
@app.delete("/admin/delete/{filename:path}")
async def remove_pdf(
    filename: str = Path(..., description="Nama file PDF, termasuk ekstensi"),
    current_admin: str = Depends(get_current_admin)
):
    delete_pdf(filename)
    delete_pdf_vectors(filename)  # Hapus vektor terkait
    return {"detail": "PDF and its vectors deleted successfully"}

# Endpoint list PDF (hanya admin)
@app.get("/admin/list")
async def get_pdf_list(current_admin: str = Depends(get_current_admin)):
    pdfs = list_pdfs()
    return pdfs

@app.get("/admin/embed/progress")
async def get_embed_progress():
    return embedding_progress

# Endpoint embedding ulang seluruh PDF
@app.post("/admin/embed")
async def embed_all_pdfs(background_tasks: BackgroundTasks, current_admin: str = Depends(get_current_admin)):
    def embed_task():
        from utils.pdf_reader import load_all_pdfs
        from utils.splitter import split_text
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import Chroma
        import time

        embedding_progress["progress"] = 0
        embedding_progress["status"] = "running"

        pdf_folder = os.path.join(os.path.dirname(__file__), "pdfs")
        pdf_texts = load_all_pdfs(pdf_folder)
        total = len(pdf_texts)
        if total == 0:
            embedding_progress["progress"] = 100
            embedding_progress["status"] = "done"
            return

        all_chunks = []
        all_metadatas = []
        processed = 0

        for filename, raw_text in pdf_texts.items():
            chunks = split_text(raw_text)
            all_chunks.extend(chunks)
            all_metadatas.extend([{"source": filename}] * len(chunks))
            processed += 1
            embedding_progress["progress"] = int(processed / total * 80)  # 80% untuk parsing

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma.from_texts(
            all_chunks,
            embedding=embeddings,
            persist_directory="vectorstore",
            metadatas=all_metadatas
        )
        vectorstore.persist()
        embedding_progress["progress"] = 100
        embedding_progress["status"] = "done"

    # Set status dan jalankan background task
    embedding_progress["progress"] = 0
    embedding_progress["status"] = "running"
    background_tasks.add_task(embed_task)
    return {"detail": "Embedding ulang sedang diproses."}
