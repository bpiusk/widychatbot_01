#  # app.py
# FastAPI backend utama untuk chatbot dan admin
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from chat_engine import get_conversation_chain_with_hybrid_multiquery_llm
from pdf_manager import save_pdf, delete_pdf, list_pdfs, list_embedded_pdfs
from auth import authenticate_admin, create_access_token, get_current_admin
import logging
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import hashlib

# Variabel global untuk progress embedding
embedding_progress = {"progress": 0, "status": "idle"}

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Konfigurasi CORS agar frontend bisa akses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model request/response untuk endpoint chat
class ChatRequest(BaseModel):
    question: str
class ChatResponse(BaseModel):
    answer: str

# Simpan conversation chain per session_id
conversation_sessions = {}

def get_session_id(request: Request):
    # Membuat session_id sederhana dari IP dan user-agent
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "unknown")
    raw = f"{ip}-{ua}"
    return hashlib.sha256(raw.encode()).hexdigest()

# Endpoint utama chatbot
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    session_id = get_session_id(req)
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = get_conversation_chain_with_hybrid_multiquery_llm(openai_api_key)
    conversation = conversation_sessions[session_id]
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

# Endpoint upload PDF
@app.post("/admin/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_admin: str = Depends(get_current_admin)
):
    save_pdf(file)
    return {"detail": "PDF uploaded successfully"}

# Endpoint hapus PDF
@app.delete("/admin/delete/{filename:path}")
async def remove_pdf(
    filename: str = Path(..., description="Nama file PDF, termasuk ekstensi"),
    current_admin: str = Depends(get_current_admin)
):
    try:
        logging.info(f"Request to delete PDF: {filename}")
        delete_pdf(filename)
        return {"detail": "PDF deleted successfully"}
    except Exception as e:
        logging.exception(f"Error deleting PDF {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Endpoint list PDF
@app.get("/admin/list")
async def get_pdf_list(current_admin: str = Depends(get_current_admin)):
    return list_pdfs()

# Endpoint list embedded PDF
@app.get("/admin/list-embedded")
async def get_embedded_pdf_list(current_admin: str = Depends(get_current_admin)):
    return list_embedded_pdfs()

# Endpoint progress embedding
@app.get("/admin/embed/progress")
async def get_embed_progress():
    return embedding_progress

# Endpoint trigger embedding ulang (background)
@app.post("/admin/embed")
async def embed_all_pdfs(background_tasks: BackgroundTasks, current_admin: str = Depends(get_current_admin)):
    from embedding_task import embed_task
    embedding_progress["progress"] = 0
    embedding_progress["status"] = "running"
    background_tasks.add_task(embed_task, embedding_progress)
    return {"detail": "Embedding ulang sedang diproses."}

# Endpoint hapus PDF & vektor
@app.delete("/admin/delete-file-and-vector/{filename:path}")
async def remove_pdf_and_vector(
    filename: str = Path(..., description="Nama file PDF, termasuk ekstensi"),
    current_admin: str = Depends(get_current_admin)
):
    try:
        logging.info(f"Request to delete PDF & vector: {filename}")
        delete_pdf(filename)
        from vector_utils import delete_vector_by_filename
        delete_vector_by_filename(filename)
        return {"detail": "PDF dan vektor berhasil dihapus"}
    except Exception as e:
        logging.exception(f"Error deleting PDF & vector {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# Endpoint hapus embedded PDF & vektor
@app.delete("/admin/delete-embedded/{filename:path}")
async def remove_embedded_pdf(
    filename: str = Path(..., description="Nama file PDF, termasuk ekstensi"),
    current_admin: str = Depends(get_current_admin)
):
    import os
    import logging
    from vector_utils import delete_vector_by_filename
    embedded_dir = os.path.join(os.path.dirname(__file__), "embedded_pdfs")
    file_path = os.path.join(embedded_dir, filename)
    try:
        logging.info(f"Request to delete embedded PDF & vector: {filename}")
        if os.path.exists(file_path):
            os.remove(file_path)
            # Hapus juga vektor berdasarkan nama file
            delete_vector_by_filename(filename)
            return {"detail": "Embedded PDF dan vektor berhasil dihapus"}
        else:
            raise Exception("File not found")
    except Exception as e:
        logging.exception(f"Error deleting embedded PDF & vector {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
