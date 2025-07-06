#pdf_reader.py
# Utility functions to read and extract text from PDF files.
# Menggunakan PyPDF2 untuk ekstraksi teks dari PDF
from PyPDF2 import PdfReader
from supabase import create_client
import os
from dotenv import load_dotenv
import io

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def load_all_pdfs():
    # Ambil daftar file dari tabel pdfs yang belum di-embedding
    res = supabase.table("pdfs").select("file_name,storage_path").eq("is_embedded", "false").execute()
    pdf_texts = {}
    for row in res.data:
        filename = row["file_name"]
        storage_path = row["storage_path"]
        # Download file dari Supabase Storage
        file_resp = supabase.storage.from_(SUPABASE_BUCKET).download(storage_path)
        file_bytes = file_resp
        with io.BytesIO(file_bytes) as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if not text.strip():
                print(f"⚠️ Tidak ada teks yang diekstrak dari {filename}")
            pdf_texts[filename] = text
    return pdf_texts