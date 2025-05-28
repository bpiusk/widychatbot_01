from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
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
        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),  # Ubah k=5
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )
    return conversation_chain
