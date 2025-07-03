#pdf_manager.py
import os
from typing import List, Dict
from fastapi import UploadFile
import shutil
import logging

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
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Gagal hapus {file_path}: {e}")
    else:
        logging.warning(f"File PDF tidak ditemukan: {file_path}")
    # Tidak perlu hapus embedded/vektor di sini

def list_pdfs() -> list:
    return [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]

def list_embedded_pdfs() -> list:
    return [f for f in os.listdir(EMBEDDED_PDF_DIR) if f.lower().endswith(".pdf")]