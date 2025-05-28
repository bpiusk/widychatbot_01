# utils/splitter.py
from langchain.text_splitter import CharacterTextSplitter

def split_text(raw_text, chunk_size=900, chunk_overlap=100):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(raw_text)
