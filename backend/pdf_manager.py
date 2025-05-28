import os
from typing import List, Dict
from fastapi import UploadFile
import shutil

PDF_DIR = os.path.join(os.path.dirname(__file__), "pdfs")
EMBEDDED_PDF_DIR = os.path.join(os.path.dirname(__file__), "embedded_pdfs")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(EMBEDDED_PDF_DIR, exist_ok=True)

def save_pdf(file: UploadFile):
    file_path = os.path.join(PDF_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # File siap untuk di-embedding

def delete_pdf(filename: str):
    # Hapus dari kedua folder jika ada
    file_path = os.path.join(PDF_DIR, filename)
    embedded_path = os.path.join(EMBEDDED_PDF_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(embedded_path):
        os.remove(embedded_path)
    # Penghapusan vektor dilakukan di load_and_embed.delete_pdf_vectors

def list_pdfs() -> list:
    return [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]