# vector_utils.py
# Fungsi utilitas untuk menghapus vektor embedding berdasarkan nama file PDF
def delete_vector_by_filename(filename):
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    import os
    from chromadb import CloudClient # Tambahkan import CloudClient
    from dotenv import load_dotenv

    # Adapter untuk Chroma embedding function
    class ChromaEmbeddingFunction:
        def __init__(self, model_name):
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.model = HuggingFaceEmbeddings(model_name=model_name)
        def __call__(self, input):
            # input: List[str]
            return self.model.embed_documents(input)

    # Muat variabel lingkungan
    load_dotenv()
    CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT = os.getenv("CHROMA_TENANT")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

    # Gunakan adapter
    embedding_function = ChromaEmbeddingFunction("sentence-transformers/all-mpnet-base-v2")

    # Inisialisasi Chroma Client untuk koneksi ke Chroma Cloud
    chroma_client = CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_COLLECTION_NAME # BARIS PENTING YANG DITAMBAHKAN
    )

    # Dapatkan koleksi dari Chroma Cloud
    collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function
    )
    
    # Hapus semua vektor yang sumbernya sesuai nama file dari Chroma Cloud
    collection.delete(where={"source": filename})