def embed_task(embedding_progress):
    from utils.pdf_reader import load_all_pdfs
    from utils.splitter import split_text
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma
    import os
    import time
    import shutil

    embedding_progress["progress"] = 0
    embedding_progress["status"] = "running"

    pdf_folder = os.path.join(os.path.dirname(__file__), "pdfs")
    embedded_folder = os.path.join(os.path.dirname(__file__), "embedded_pdfs")
    if not os.path.exists(embedded_folder):
        os.makedirs(embedded_folder)

    pdf_texts = load_all_pdfs(pdf_folder)
    total = len(pdf_texts)
    if total == 0:
        embedding_progress["progress"] = 100
        embedding_progress["status"] = "done"
        return

    all_chunks = []
    all_metadatas = []
    processed = 0

    for filename, raw_text in pdf_texts.items():
        chunks = split_text(raw_text)
        all_chunks.extend(chunks)
        all_metadatas.extend([
            {"source": filename, "text": chunk, "chunk_index": idx}
            for idx, chunk in enumerate(chunks)
        ])
        processed += 1
        embedding_progress["progress"] = int(processed / total * 80)
        # Pindahkan file PDF ke embedded_pdfs setelah selesai di-embedding
        src_path = os.path.join(pdf_folder, filename)
        dst_path = os.path.join(embedded_folder, filename)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = Chroma.from_texts(
        all_chunks,
        embedding=embeddings,
        persist_directory="vectorstore",
        metadatas=all_metadatas
    )
    vectorstore.persist()
    embedding_progress["progress"] = 100
    embedding_progress["status"] = "done"
