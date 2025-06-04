from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from utils.postprocess import postprocess_context, postprocess_answer

# --- INISIALISASI SEKALI DI AWAL ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
llm = None  # Akan diinisialisasi saat ada API key
with open("prompts/rag_prompt.txt", "r", encoding="utf-8") as f:
    rag_template = f.read()
QA_PROMPT = PromptTemplate(
    template=rag_template,
    input_variables=["context", "question"]
)


def get_conversation_chain_with_hybrid_multiquery_llm(openai_api_key, n_paraphrase=3, alpha=0.5, top_k=5):
    global llm
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Ambil semua chunk text dan simpan vectorizer global (cache di memory, update jika vectorstore berubah)
    all_metadatas = vectorstore._collection.get(include=["metadatas"])
    chunk_texts = [meta['text'] for meta in all_metadatas['metadatas'] if 'text' in meta]
    if not chunk_texts:
        raise ValueError("Tidak ada chunk text di vectorstore!")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunk_texts)

    def generate_paraphrases(question, n=n_paraphrase):
        para_llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.3)
        prompt = (
            f"Buat {n} parafrase berbeda untuk pertanyaan berikut dalam bahasa Indonesia. "
            f"Pisahkan setiap parafrase dengan baris baru.\nPertanyaan: {question}\nParafrase:"
        )
        result = para_llm.predict(prompt)
        return [question] + [p.strip() for p in result.split('\n') if p.strip()]

    def hybrid_multiquery_retrieve(question, top_k=top_k, alpha=alpha):
        multi_queries = generate_paraphrases(question, n=n_paraphrase)
        print("Multiquery (paraphrase) yang digunakan:", multi_queries)
        # Skor hybrid untuk setiap chunk, dari semua parafrase
        all_scores = []
        all_embeddings = vectorstore._collection.get(include=["embeddings"])["embeddings"]
        for q in multi_queries:
            # TF-IDF
            query_tfidf = vectorizer.transform([q])
            tfidf_scores = (tfidf_matrix * query_tfidf.T).toarray().flatten()
            # Vector
            q_emb = embeddings.embed_query(q)
            vector_scores = [
                np.dot(q_emb, np.array(doc_emb)) / (np.linalg.norm(q_emb) * np.linalg.norm(doc_emb))
                for doc_emb in all_embeddings
            ]
            # Hybrid
            hybrid_scores = alpha * tfidf_scores + (1 - alpha) * np.array(vector_scores)
            all_scores.append(hybrid_scores)
            print(f"\nQuery: {q}")
            print("TF-IDF scores (top 3):", sorted(tfidf_scores, reverse=True)[:3])
            print("Vector scores (top 3):", sorted(vector_scores, reverse=True)[:3])
        # Gabungkan skor: ambil skor tertinggi untuk setiap chunk di semua parafrase
        all_scores = np.array(all_scores)
        final_scores = np.max(all_scores, axis=0)
        top_idx = np.argsort(final_scores)[::-1][:top_k]
        all_metas = all_metadatas['metadatas']
        docs = []
        for idx in top_idx:
            print(f"Hybrid score: {final_scores[idx]:.4f}")
            print("Chunk:", all_metas[idx].get('text', '')[:200])  # tampilkan 200 karakter pertama
            class Doc:
                def __init__(self, meta):
                    self.page_content = meta.get('text', '')
            docs.append(Doc(all_metas[idx]))
        return docs

    class HybridMultiQueryLLMConversationalRetrievalChain:
        def __init__(self, llm, memory, prompt):
            self.llm = llm
            self.memory = memory
            self.prompt = prompt
        def __call__(self, inputs):
            question = inputs["question"]
            docs = hybrid_multiquery_retrieve(question, top_k=top_k, alpha=alpha)
            context = "\n".join([d.page_content for d in docs])
            context = postprocess_context(context)  # Post-processing context sebelum ke LLM
            prompt_str = self.prompt.format(context=context, question=question)
            answer = self.llm.predict(prompt_str)
            answer = postprocess_answer(answer)  # Post-processing jawaban sebelum ke user
            self.memory.save_context({"input": question}, {"output": answer})
            return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

    return HybridMultiQueryLLMConversationalRetrievalChain(llm, memory, QA_PROMPT)
