import os
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from utils.pdf_reader import load_all_pdfs
from utils.splitter import split_text

load_dotenv()

def delete_pdf_vectors(filename):
    """
    Menghapus semua vektor yang berasal dari file PDF tertentu dari vectorstore.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="vectorstore",
        embedding_function=embeddings
    )
    docs = vectorstore.get(include=['metadatas', 'ids'])
    ids_to_delete = [
        doc_id for doc_id, meta in zip(docs['ids'], docs['metadatas'])
        if meta.get('source') == filename
    ]
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)
        vectorstore.persist()
        print(f"✅ Vektor dari '{filename}' berhasil dihapus dari vectorstore.")
    else:
        print(f"⚠️ Tidak ditemukan vektor untuk '{filename}'.")

def embed_single_pdf(filepath, filename):
    """
    Embedding satu file PDF ke vectorstore.
    """
    from utils.pdf_reader import load_pdf
    from utils.splitter import split_text
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="vectorstore",
        embedding_function=embeddings
    )
    raw_text = load_pdf(filepath)
    chunks = split_text(raw_text)
    metadatas = [{"source": filename}] * len(chunks)
    vectorstore.add_texts(chunks, metadatas=metadatas)
    vectorstore.persist()
    print(f"✅ Embedding selesai untuk {filename}")

if __name__ == "__main__":
    pdf_folder = "pdfs"  # Ganti dari "data" ke "pdfs"
    pdf_texts = load_all_pdfs(pdf_folder)  # {'file1.pdf': '...', ...}

    all_chunks = []
    all_metadatas = []

    for filename, raw_text in pdf_texts.items():
        print(f"Memproses {filename}, panjang teks: {len(raw_text)} karakter")
        chunks = split_text(raw_text)
        print(f"Jumlah chunk dari {filename}: {len(chunks)}")
        all_chunks.extend(chunks)
        all_metadatas.extend([{"source": filename}] * len(chunks))

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        persist_directory="vectorstore",
        metadatas=all_metadatas
    )
    vectorstore.persist()

    print("✅ Vectorstore berhasil dibuat dan disimpan ke folder 'vectorstore'.")
