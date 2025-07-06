# embed_task.py
# Fungsi background task untuk proses embedding ulang semua PDF

def embed_task(embedding_progress, chroma_api_key, chroma_tenant, chroma_collection_name):
    from utils.pdf_reader import load_all_pdfs
    from utils.splitter import split_text
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    import os
    import re
    from chromadb import CloudClient
    import datetime
    from supabase import create_client
    from dotenv import load_dotenv

    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Set status progress
    embedding_progress["progress"] = 0
    embedding_progress["status"] = "running"

    # Ambil semua PDF dari Supabase Storage
    pdf_texts = load_all_pdfs()
    total = len(pdf_texts)
    if total == 0:
        embedding_progress["progress"] = 100
        embedding_progress["status"] = "done"
        return

    all_chunks = []
    all_metadatas = []
    all_ids = []
    processed = 0

    # Proses setiap file PDF
    for filename, raw_text in pdf_texts.items():
        chunks = split_text(raw_text)
        all_chunks.extend(chunks)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        for idx, chunk in enumerate(chunks):
            tag_match = re.search(r'Tag:\s*(.*)', chunk)
            tags = [t.strip() for t in tag_match.group(1).split(',')] if tag_match else []
            metadata = {
                "source": filename,
                "chunk_index": idx,
                "tags": ", ".join(tags) if tags else ""
            }
            all_metadatas.append(metadata)
            # Buat ID unik: filename-timestamp-idx
            chunk_id = f"{filename}-{timestamp}-{idx}"
            all_ids.append(chunk_id)
        processed += 1
        embedding_progress["progress"] = int(processed / total * 80)

    # Proses embedding dan simpan vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Inisialisasi Chroma Client untuk koneksi ke Chroma Cloud
    chroma_client = CloudClient(
        api_key=chroma_api_key,
        tenant=chroma_tenant,
        database=chroma_collection_name
    )

    # Membuat dan menyimpan vectorstore dari semua chunk ke cloud
    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        client=chroma_client,
        collection_name=chroma_collection_name,
        metadatas=all_metadatas,
        ids=all_ids
    )

    # Update status is_embedded di tabel pdfs
    for filename in pdf_texts.keys():
        supabase.table("pdfs").update({"is_embedded": "true"}).eq("file_name", filename).execute()

    embedding_progress["progress"] = 100
    embedding_progress["status"] = "done"