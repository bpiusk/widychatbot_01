# load_and_embed.py
# Script untuk memuat semua PDF, memecah menjadi chunk, dan membuat vectorstore embedding
import os
import re
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from utils.pdf_reader import load_all_pdfs
from utils.splitter import split_text
from chromadb import CloudClient
from dotenv import load_dotenv

# Muat variabel lingkungan dari .env
load_dotenv()
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

if __name__ == "__main__":
    # Inisialisasi Chroma CloudClient dari environment variable
    client = CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_COLLECTION_NAME
    )

    # Ambil semua file PDF dari Supabase Storage, bukan dari folder lokal
    pdf_texts = load_all_pdfs()  # <-- Hapus argumen pdf_folder

    all_chunks = []
    all_metadatas = []

    # Proses setiap file PDF
    for filename, raw_text in pdf_texts.items():
        print(f"Memproses {filename}, panjang teks: {len(raw_text)} karakter")
        chunks = split_text(raw_text)
        print(f"Jumlah chunk dari {filename}: {len(chunks)}")  # Log jumlah chunk
        all_chunks.extend(chunks)
        for idx, chunk in enumerate(chunks):
            tag_match = re.search(r'Tag:\s*(.*)', chunk)
            tags = [t.strip() for t in tag_match.group(1).split(',')] if tag_match else []
            # Metadata untuk setiap chunk
            metadata = {
                "source": filename,
                "chunk_index": idx,
                "tags": ", ".join(tags) if tags else ""
            }
            all_metadatas.append(metadata)

    if all_metadatas:
        print("Contoh metadata:", all_metadatas[0])
    else:
        print("Tidak ada metadata yang dihasilkan.")

    print("Contoh chunk:", all_chunks[0] if all_chunks else "TIDAK ADA CHUNK")

    # Inisialisasi model embedding
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Gunakan client hasil inisialisasi di atas
    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        client=client,
        collection_name=CHROMA_COLLECTION_NAME,
        metadatas=all_metadatas
    )

    print("Vectorstore berhasil dibuat dan disimpan ke Chroma Cloud.")