from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- INISIALISASI SEKALI DI AWAL ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
llm = None  # Akan diinisialisasi saat ada API key
with open("prompts/rag_prompt.txt", "r", encoding="utf-8") as f:
    rag_template = f.read()
QA_PROMPT = PromptTemplate(
    template=rag_template,
    input_variables=["context", "question"]
)

def get_conversation_chain(openai_api_key):
    global llm
    # Inisialisasi LLM hanya jika belum ada atau API key berubah
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0.3)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    from langchain.chains import ConversationalRetrievalChain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )
    return conversation_chain

def get_conversation_chain_with_paraphrase(openai_api_key):
    global llm
    if llm is None or getattr(llm, "openai_api_key", None) != openai_api_key:
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def retrieve_with_paraphrase(question):
        # Step 1: Paraphrase the question using GPT-3.5
        para_llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
        prompt = f"Parafrasekan pertanyaan berikut ke dalam bahasa Indonesia yang berbeda, tetap dengan makna yang sama.\nPertanyaan: {question}\nParafrase:"
        para_result = para_llm.predict(prompt)
        paraphrased = para_result.strip()
        # Step 2: Retrieve context for both original and paraphrased
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs1 = retriever.get_relevant_documents(question)
        docs2 = retriever.get_relevant_documents(paraphrased)
        # Gabungkan dan hilangkan duplikat
        all_docs = {d.page_content: d for d in docs1 + docs2}
        return list(all_docs.values())

    class MultiQueryConversationalRetrievalChain:
        def __init__(self, llm, memory, prompt):
            self.llm = llm
            self.memory = memory
            self.prompt = prompt
        def __call__(self, inputs):
            question = inputs["question"]
            docs = retrieve_with_paraphrase(question)
            context = "\n".join([d.page_content for d in docs])
            # Gunakan prompt custom
            prompt_str = self.prompt.format(context=context, question=question)
            answer = self.llm.predict(prompt_str)
            # Simpan ke memory jika perlu
            self.memory.save_context({"input": question}, {"output": answer})
            return {"answer": answer, "chat_history": self.memory.chat_memory.messages}

    return MultiQueryConversationalRetrievalChain(llm, memory, QA_PROMPT)
