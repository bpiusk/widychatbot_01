# Script untuk memuat semua PDF, memecah menjadi chunk, dan membuat vectorstore embedding
import os
import re
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from utils.pdf_reader import load_all_pdfs
from utils.splitter import split_text

load_dotenv()

if __name__ == "__main__":
    # Folder PDF sumber
    pdf_folder = "pdfs" 
    # Memuat semua file PDF dan mengembalikan dict {filename: text}
    pdf_texts = load_all_pdfs(pdf_folder)

    all_chunks = []
    all_metadatas = []

    # Proses setiap file PDF
    for filename, raw_text in pdf_texts.items():
        print(f"Memproses {filename}, panjang teks: {len(raw_text)} karakter")
        # Memecah teks PDF menjadi chunk kecil
        chunks = split_text(raw_text)
        print(f"Jumlah chunk dari {filename}: {len(chunks)}")
        all_chunks.extend(chunks)
        for idx, chunk in enumerate(chunks):
            # Ekstrak tag jika ada
            tag_match = re.search(r'Tag:\s*(.*)', chunk)
            tags = [t.strip() for t in tag_match.group(1).split(',')] if tag_match else []
            # Metadata untuk setiap chunk
            metadata = {
                "source": filename,
                "text": chunk,
                "chunk_index": idx,
                "tags": ", ".join(tags) if tags else ""
            }
            all_metadatas.append(metadata)

    if all_metadatas:
        print("Contoh metadata:", all_metadatas[0])
    else:
        print("Tidak ada metadata yang dihasilkan.")

    print("Contoh chunk:", chunks[0] if chunks else "TIDAK ADA CHUNK")

    # Inisialisasi model embedding
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Membuat dan menyimpan vectorstore dari semua chunk
    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        persist_directory="vectorstore",
        metadatas=all_metadatas
    )
    vectorstore.persist()

    print("Vectorstore berhasil dibuat dan disimpan ke folder 'vectorstore'.")