#pdf_reader.py
# Utility functions to read and extract text from PDF files.
# Menggunakan PyPDF2 untuk ekstraksi teks dari PDF
from PyPDF2 import PdfReader
import os

def load_all_pdfs(folder_path):
    pdf_texts = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            with open(os.path.join(folder_path, filename), "rb") as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                # Tambahkan log jika teks kosong
                if not text.strip():
                    print(f"⚠️ Tidak ada teks yang diekstrak dari {filename}")
                pdf_texts[filename] = text
    return pdf_texts
