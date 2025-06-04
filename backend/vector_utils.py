def delete_vector_by_filename(filename):
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
    import os
    from contextlib import contextmanager
    @contextmanager
    def chroma_context(*args, **kwargs):
        vectorstore = Chroma(*args, **kwargs)
        try:
            yield vectorstore
        finally:
            del vectorstore
            import gc
            gc.collect()
    vectorstore_dir = os.path.join(os.path.dirname(__file__), "vectorstore")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    with chroma_context(persist_directory=vectorstore_dir, embedding_function=embeddings) as vectorstore:
        vectorstore.delete(where={"source": filename})
