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
from chromadb import CloudClient

# Muat variabel lingkungan di awal file untuk akses global
load_dotenv()
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")

if not CHROMA_API_KEY or not CHROMA_TENANT or not CHROMA_COLLECTION_NAME:
    raise RuntimeError(
        "CHROMA_API_KEY, CHROMA_TENANT, dan CHROMA_COLLECTION_NAME harus di-set di environment (.env)"
    )

# --- INISIALISASI SEKALI DI AWAL ---
# Inisialisasi model embedding
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

try:
    # Inisialisasi Chroma Client untuk koneksi ke Chroma Cloud
    chroma_client = CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_COLLECTION_NAME # BARIS PENTING YANG DITAMBAHKAN
    )

    # Dapatkan koleksi yang sudah ada dari Chroma Cloud
    vectorstore = Chroma(
        client=chroma_client,
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings
    )
    print(f"DEBUG: Menggunakan koleksi Chroma Cloud: {CHROMA_COLLECTION_NAME}")
except Exception as e:
    raise RuntimeError(f"Gagal inisialisasi Chroma CloudClient/vectorstore: {e}")

llm = None
with open("prompts/rag_prompt.txt", "r", encoding="utf-8") as f:
    rag_template = f.read()
QA_PROMPT = PromptTemplate(
    template=rag_template,
    input_variables=["context", "question"]
)

# Fungsi utama untuk membuat conversation chain dengan hybrid multiquery LLM
# n_paraphrase: jumlah parafrase, alpha: bobot hybrid, top_k: jumlah chunk diambil

def get_conversation_chain_with_hybrid_multiquery_llm(openai_api_key, n_paraphrase=3, alpha=0.4, top_k=10):
    global llm
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.3)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Ambil semua chunk dari Chroma Cloud dengan paging (limit+offset)
    collection = vectorstore._collection
    # print(f"DEBUG: Paging koleksi Chroma: {collection.name}")
    total = collection.count()
    # print(f"DEBUG: Total chunk di koleksi: {total}")
    batch_size = 100
    all_documents = []
    all_metadatas = []
    all_embeddings = []
    for offset in range(0, total, batch_size):
        batch = collection.get(
            include=["documents", "metadatas", "embeddings"],
            limit=batch_size,
            offset=offset
        )
        all_documents.extend(batch["documents"])
        all_metadatas.extend(batch["metadatas"])
        all_embeddings.extend(batch["embeddings"])
    # DEBUG: Print nama file/source dari semua chunk yang diambil
    sources = set()
    for meta in all_metadatas:
        src = meta.get("source", None)
        if src:
            sources.add(src)
    # print(f"DEBUG: Nama file/source yang ditemukan di koleksi: {sorted(list(sources))}")
    # print(f"DEBUG: Jumlah file unik: {len(sources)}")
    
    # Sinkronisasi jumlah chunk dan embedding
    min_len = min(len(all_documents), len(all_embeddings))
    chunk_texts = all_documents[:min_len]
    all_metadatas = all_metadatas[:min_len]
    all_embeddings = all_embeddings[:min_len]

    if not chunk_texts:
        raise ValueError("Tidak ada chunk text di vectorstore!")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunk_texts)

    # Membuat parafrase pertanyaan
    def generate_paraphrases(question, n=n_paraphrase):
        para_llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.3)
        prompt = (
            f"Buat {n} parafrase berbeda untuk pertanyaan berikut dalam bahasa Indonesia. "
            f"Pisahkan setiap parafrase dengan baris baru.\nPertanyaan: {question}\nParafrase:"
        )
        result = para_llm.predict(prompt)
        return [question] + [p.strip() for p in result.split('\n') if p.strip()]

    # Format riwayat chat menjadi string
    def format_history(chat_history, last_question=None, max_history=4):
        # Ambil hanya max_history pesan terakhir
        history_lines = []
        for msg in chat_history[-max_history:]:
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
        # print("Multiquery (paraphrase) yang digunakan:", multi_queries)
        all_scores = []
        # Jangan ambil ulang all_embeddings, gunakan yang sudah dipaging!
        question_embeddings = []
        for q in multi_queries:
            query_tfidf = vectorizer.transform([q])
            tfidf_scores = (tfidf_matrix * query_tfidf.T).toarray().flatten()
            q_emb = embeddings.embed_query(q)
            question_embeddings.append(q_emb)
            vector_scores = [
                np.dot(q_emb, np.array(all_embeddings[i])) / (np.linalg.norm(q_emb) * np.linalg.norm(all_embeddings[i]))
                for i in range(len(all_embeddings))
            ]
            # Pastikan tfidf_scores dan vector_scores sama panjang
            if len(tfidf_scores) != len(vector_scores):
                min_len = min(len(tfidf_scores), len(vector_scores))
                tfidf_scores = tfidf_scores[:min_len]
                vector_scores = vector_scores[:min_len]
            # hybrid_scores = alpha * tfidf_scores + (1 - alpha) * np.array(vector_scores)
            # Dengan alpha kecil, cosine similarity lebih dominan
            hybrid_scores = alpha * tfidf_scores + (1 - alpha) * np.array(vector_scores)
            all_scores.append(hybrid_scores)
            # print(f"\nQuery: {q}")
            # print("TF-IDF scores (top 3):", sorted(tfidf_scores, reverse=True)[:3])
            # print("Vector scores (top 3):", sorted(vector_scores, reverse=True)[:3])
        # Gabungkan skor: ambil skor tertinggi untuk setiap chunk di semua parafrase
        all_scores = np.array(all_scores)
        final_scores = np.max(all_scores, axis=0)
        top_idx = np.argsort(final_scores)[::-1][:top_k]
        all_metas = all_metadatas

        # docs diurutkan sesuai urutan hybrid score (top_idx)
        docs = []
        for idx in top_idx:
            # print(f"Hybrid score: {final_scores[idx]:.4f}")
            # print("Chunk:", all_metas[idx].get('text', '')[:200])
            source_file = all_metas[idx].get('source', 'Tidak diketahui')
            # print(f"File PDF terpilih: {source_file}")
            # print(f"Cosine similarity (vector): {np.dot(embeddings.embed_query(question), np.array(all_embeddings[idx])) / (np.linalg.norm(embeddings.embed_query(question)) * np.linalg.norm(all_embeddings[idx]) + 1e-8):.4f}")
            class Doc:
                def __init__(self, meta, text):
                    self.page_content = text
                    self.source = meta.get('source', '')
                    self.hybrid_score = final_scores[idx]
                    self.cosine_similarity = np.dot(embeddings.embed_query(question), np.array(all_embeddings[idx])) / (np.linalg.norm(embeddings.embed_query(question)) * np.linalg.norm(all_embeddings[idx]) + 1e-8)
            docs.append(Doc(all_metas[idx], chunk_texts[idx]))
        
        # Setelah final_scores dan sebelum top_idx
        # print("\n=== DEBUG: Skor hybrid dan cosine similarity untuk chunk dari file terbaru ===")
        latest_file = sorted(list(sources))[-1]  # Ambil file terakhir secara alfabet (atau tentukan manual)
        q_emb_debug = embeddings.embed_query(question)
        for idx, meta in enumerate(all_metadatas):
            if meta.get("source") == latest_file and idx < len(all_embeddings):
                cos_sim = np.dot(q_emb_debug, np.array(all_embeddings[idx])) / (np.linalg.norm(q_emb_debug) * np.linalg.norm(all_embeddings[idx]) + 1e-8)
                # print(f"IDX: {idx} | FILE: {latest_file} | Hybrid: {final_scores[idx]:.4f} | Cosine: {cos_sim:.4f} | CHUNK: {chunk_texts[idx][:80]}")
        
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
            # Batasi panjang context (misal, max 4000 karakter)
            context = "\n".join([d.page_content[:1000] for d in docs])  # potong tiap chunk max 1000 char
            context = postprocess_context(context)

            # Gabungkan riwayat chat (hanya max_history terakhir)
            full_history = format_history(chat_history, last_question=question, max_history=8)
            prompt_str = self.prompt.format(context=context, question=full_history)
            answer = self.llm.predict(prompt_str)
            answer = postprocess_answer(answer)

            self.memory.save_context({"input": question}, {"output": answer})
            return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

    return HybridMultiQueryLLMConversationalRetrievalChain(llm, memory, QA_PROMPT)