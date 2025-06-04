import re

def postprocess_context(context: str) -> str:
    """
    Bersihkan context sebelum masuk ke LLM.
    - Hapus tag 'Tag:' dan isinya
    - Hilangkan whitespace berlebih
    """
    # Hapus baris Tag: ...
    context = re.sub(r'Tag:.*', '', context)
    # Hapus whitespace berlebih
    context = re.sub(r'\n+', '\n', context)
    context = context.strip()
    return context


def postprocess_answer(answer: str) -> str:
    """
    Bersihkan jawaban dari LLM sebelum dikirim ke user.
    - Hilangkan duplikasi baris
    - Hilangkan whitespace berlebih
    - (Opsional) Format ulang jika perlu
    """
    # Hilangkan duplikasi baris
    lines = answer.splitlines()
    seen = set()
    cleaned = []
    for line in lines:
        l = line.strip()
        if l and l not in seen:
            cleaned.append(l)
            seen.add(l)
    return '\n'.join(cleaned)
