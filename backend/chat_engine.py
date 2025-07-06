# Modul utama untuk logika retrieval dan chat engine chatbot
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from utils.postprocess import postprocess_context, postprocess_answer
import os
from dotenv import load_dotenv
from chromadb import CloudClient # Tambahkan import CloudClient

# Muat variabel lingkungan di awal file untuk akses global
load_dotenv()
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

# --- INISIALISASI SEKALI DI AWAL ---
# Inisialisasi model embedding
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Inisialisasi Chroma Client untuk koneksi ke Chroma Cloud
chroma_client = CloudClient(
    api_key=CHROMA_API_KEY,
    tenant=CHROMA_TENANT,
    database=CHROMA_COLLECTION_NAME # BARIS PENTING YANG DITAMBAHKAN
)

# Dapatkan koleksi yang sudah ada dari Chroma Cloud
vectorstore = Chroma(
    client=chroma_client,
    collection_name=CHROMA_COLLECTION_NAME, # collection_name juga tetap di sini
    embedding_function=embeddings
)

llm = None
with open("prompts/rag_prompt.txt", "r", encoding="utf-8") as f:
    rag_template = f.read()
QA_PROMPT = PromptTemplate(
    template=rag_template,
    input_variables=["context", "question"]
)

# Fungsi utama untuk membuat conversation chain dengan hybrid multiquery LLM
# n_paraphrase: jumlah parafrase, alpha: bobot hybrid, top_k: jumlah chunk diambil

def get_conversation_chain_with_hybrid_multiquery_llm(openai_api_key, n_paraphrase=8, alpha=0.6, top_k=15):
    global llm
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.5)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Ambil semua chunk text dan simpan vectorizer global (cache di memory, update jika vectorstore berubah)
    all_docs = vectorstore._collection.get(include=["documents", "metadatas"])
    chunk_texts = all_docs['documents']
    all_metadatas = all_docs['metadatas']
    if not chunk_texts:
        raise ValueError("Tidak ada chunk text di vectorstore!")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunk_texts)

    # Membuat parafrase pertanyaan
    def generate_paraphrases(question, n=n_paraphrase):
        para_llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.6)
        prompt = (
            f"Buat {n} parafrase berbeda untuk pertanyaan berikut dalam bahasa Indonesia. "
            f"Pisahkan setiap parafrase dengan baris baru.\nPertanyaan: {question}\nParafrase:"
        )
        result = para_llm.predict(prompt)
        return [question] + [p.strip() for p in result.split('\n') if p.strip()]

    # Format riwayat chat menjadi string
    def format_history(chat_history, last_question=None):
        history_lines = []
        for msg in chat_history:
            if hasattr(msg, "type"):
                if msg.type == "human":
                    history_lines.append(f"User: {msg.content}")
                elif msg.type == "ai":
                    history_lines.append(f"Bot: {msg.content}")
            elif hasattr(msg, "role"):
                if msg.role == "user":
                    history_lines.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    history_lines.append(f"Bot: {msg.content}")
        if last_question:
            history_lines.append(f"User: {last_question}")
        return "\n".join(history_lines).strip()

    # Hybrid multiquery retrieval: menggabungkan tf-idf dan vector similarity
    def hybrid_multiquery_retrieve(question, chat_history=None, top_k=top_k, alpha=alpha):
        question_for_retrieval = format_history(chat_history, last_question=question) if chat_history else question
        multi_queries = generate_paraphrases(question_for_retrieval, n=n_paraphrase)
        print("Multiquery (paraphrase) yang digunakan:", multi_queries)
        all_scores = []
        all_embeddings = vectorstore._collection.get(include=["embeddings"])["embeddings"]
        question_embeddings = []
        for q in multi_queries:
            query_tfidf = vectorizer.transform([q])
            tfidf_scores = (tfidf_matrix * query_tfidf.T).toarray().flatten()
            q_emb = embeddings.embed_query(q)
            question_embeddings.append(q_emb)
            vector_scores = [
                np.dot(q_emb, np.array(doc_emb)) / (np.linalg.norm(q_emb) * np.linalg.norm(doc_emb))
                for doc_emb in all_embeddings
            ]
            hybrid_scores = alpha * tfidf_scores + (1 - alpha) * np.array(vector_scores)
            all_scores.append(hybrid_scores)
            print(f"\nQuery: {q}")
            print("TF-IDF scores (top 3):", sorted(tfidf_scores, reverse=True)[:3])
            print("Vector scores (top 3):", sorted(vector_scores, reverse=True)[:3])
        # Gabungkan skor: ambil skor tertinggi untuk setiap chunk di semua parafrase
        all_scores = np.array(all_scores)
        final_scores = np.max(all_scores, axis=0)
        top_idx = np.argsort(final_scores)[::-1][:top_k]
        all_metas = all_metadatas
        docs = []
        for idx in top_idx:
            print(f"Hybrid score: {final_scores[idx]:.4f}")
            print("Chunk:", all_metas[idx].get('text', '')[:200])
            source_file = all_metas[idx].get('source', 'Tidak diketahui')
            print(f"File PDF terpilih: {source_file}")
            print(f"Cosine similarity (vector): {vector_scores[idx]:.4f}")
            print("Vektor embedding pertanyaan (10 angka pertama):", np.array(question_embeddings[0])[:10])
            print("Vektor embedding dokumen terpilih (10 angka pertama):", np.array(all_embeddings[idx])[:10])
            class Doc:
                def __init__(self, meta, text):
                    self.page_content = text
                    self.source = meta.get('source', '')
                    self.hybrid_score = final_scores[idx]
                    self.cosine_similarity = vector_scores[idx]
            docs.append(Doc(all_metas[idx], chunk_texts[idx]))
        return docs

    # Kelas chain retrieval + LLM
    class HybridMultiQueryLLMConversationalRetrievalChain:
        def __init__(self, llm, memory, prompt):
            self.llm = llm
            self.memory = memory
            self.prompt = prompt

        def _is_meta_question(self, question):
            # Deteksi pertanyaan meta (tentang kemampuan bot)
            meta_patterns = [
                "informasi yang kamu miliki",
                "apa yang bisa kamu lakukan",
                "pengetahuan apa saja",
                "bisa bantu apa",
                "apa kemampuan kamu",
                "apa saja yang kamu tahu",
                "apa yang kamu tahu"
            ]
            q_lower = question.lower()
            return any(p in q_lower for p in meta_patterns)

        def _meta_answer(self):
            # Jawaban khusus untuk pertanyaan meta
            return (
                "Saya adalah asisten virtual yang dapat membantu menjawab pertanyaan seputar dokumen yang telah diunggah, "
                "termasuk ringkasan, penjelasan, pencarian informasi, dan tanya jawab terkait isi dokumen. "
                "Silakan ajukan pertanyaan spesifik mengenai topik atau dokumen yang Anda inginkan."
            )

        def __call__(self, inputs):
            question = inputs["question"]
            chat_history = self.memory.chat_memory.messages if hasattr(self.memory, "chat_memory") else []

            # Cek jika pertanyaan adalah meta-question
            if self._is_meta_question(question):
                answer = self._meta_answer()
                self.memory.save_context({"input": question}, {"output": answer})
                return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

            # Gunakan seluruh riwayat untuk retrieval
            docs = hybrid_multiquery_retrieve(question, chat_history=chat_history, top_k=top_k, alpha=alpha)
            context = "\n".join([d.page_content for d in docs])
            context = postprocess_context(context)

            # Gabungkan seluruh riwayat ke prompt LLM
            full_history = format_history(chat_history, last_question=question)
            prompt_str = self.prompt.format(context=context, question=full_history)
            answer = self.llm.predict(prompt_str)
            answer = postprocess_answer(answer)

            self.memory.save_context({"input": question}, {"output": answer})
            return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

    return HybridMultiQueryLLMConversationalRetrievalChain(llm, memory, QA_PROMPT)