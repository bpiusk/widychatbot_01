import re

def split_text(raw_text):
    
    pattern = r'(Pertanyaan:.*?Jawaban:.*?(?:Tag:.*)?)(?=Pertanyaan:|$)'

    chunks = re.findall(pattern, raw_text, re.DOTALL)
    return [chunk.strip() for chunk in chunks if chunk.strip()]
