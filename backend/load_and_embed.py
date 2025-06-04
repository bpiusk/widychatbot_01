import os
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from utils.pdf_reader import load_all_pdfs
from utils.splitter import split_text

load_dotenv()

if __name__ == "__main__":
    pdf_folder = "pdfs" 
    pdf_texts = load_all_pdfs(pdf_folder)

    all_chunks = []
    all_metadatas = []

    for filename, raw_text in pdf_texts.items():
        print(f"Memproses {filename}, panjang teks: {len(raw_text)} karakter")
        chunks = split_text(raw_text)
        print(f"Jumlah chunk dari {filename}: {len(chunks)}")
        all_chunks.extend(chunks)
        all_metadatas.extend([
            {"source": filename, "text": chunk} for chunk in chunks
        ])

    if all_metadatas:
        print("Contoh metadata:", all_metadatas[0])
    else:
        print("Tidak ada metadata yang dihasilkan.")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        persist_directory="vectorstore",
        metadatas=all_metadatas
    )
    vectorstore.persist()

    print("Vectorstore berhasil dibuat dan disimpan ke folder 'vectorstore'.")