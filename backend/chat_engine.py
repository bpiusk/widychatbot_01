from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

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


def get_conversation_chain_with_multiquery_llm(openai_api_key):
    global llm
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def generate_paraphrases(question, n=3):
        para_llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.3)
        prompt = (
            f"Buat {n} parafrase berbeda untuk pertanyaan berikut dalam bahasa Indonesia. "
            f"Pisahkan setiap parafrase dengan baris baru.\nPertanyaan: {question}\nParafrase:"
        )
        result = para_llm.predict(prompt)
        # Gabungkan pertanyaan asli dan parafrase hasil LLM
        return [question] + [p.strip() for p in result.split('\n') if p.strip()]

    def retrieve_with_multiquery_llm(question):
        multi_queries = generate_paraphrases(question, n=3)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        all_docs = {}
        for q in multi_queries:
            docs = retriever.get_relevant_documents(q)
            for d in docs:
                all_docs[d.page_content] = d
        return list(all_docs.values())

    class MultiQueryLLMConversationalRetrievalChain:
        def __init__(self, llm, memory, prompt):
            self.llm = llm
            self.memory = memory
            self.prompt = prompt
        def __call__(self, inputs):
            question = inputs["question"]
            docs = retrieve_with_multiquery_llm(question)
            context = "\n".join([d.page_content for d in docs])
            prompt_str = self.prompt.format(context=context, question=question)
            answer = self.llm.predict(prompt_str)
            self.memory.save_context({"input": question}, {"output": answer})
            return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

    return MultiQueryLLMConversationalRetrievalChain(llm, memory, QA_PROMPT)
