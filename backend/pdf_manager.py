#pdf_manager.py
import os
from fastapi import UploadFile
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def save_pdf(file: UploadFile):
    # Upload file ke Supabase Storage
    file_bytes = file.file.read()
    storage_path = f"{file.filename}"
    supabase.storage.from_(SUPABASE_BUCKET).upload(storage_path, file_bytes, {"content-type": "application/pdf"})
    # Insert metadata ke tabel pdfs
    now = datetime.utcnow().isoformat()
    supabase.table("pdfs").insert({
        "file_name": file.filename,
        "storage_path": storage_path,
        "uploud_at": now,
        "is_embedded": "false"  # <-- string, bukan boolean
    }).execute()

def delete_pdf(filename: str):
    # Hapus file dari Supabase Storage
    storage_path = filename
    supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
    # Hapus metadata dari tabel pdfs
    supabase.table("pdfs").delete().eq("file_name", filename).execute()

def list_pdfs() -> list:
    # Ambil daftar PDF dari tabel pdfs yang belum di-embedding
    res = supabase.table("pdfs").select("file_name").eq("is_embedded", "false").execute()  # <-- string
    return [row["file_name"] for row in res.data] if res.data else []

def list_embedded_pdfs() -> list:
    # Ambil daftar PDF dari tabel pdfs yang sudah di-embedding
    res = supabase.table("pdfs").select("file_name").eq("is_embedded", "true").execute()  # <-- string
    return [row["file_name"] for row in res.data] if res.data else []