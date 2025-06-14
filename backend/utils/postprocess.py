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
    # Gabungkan baris kosong berlebih
    answer = re.sub(r'\n{3,}', '\n\n', answer)
    lines = answer.splitlines()
    cleaned = []
    seen = set()
    for line in lines:
        l = line.rstrip()
        # Jangan deduplikasi jika baris diawali nomor (1. ...), selalu pertahankan urutan
        if re.match(r'^\s*\d+\.', l):
            cleaned.append(line)
        elif l and l not in seen:
            cleaned.append(line)
            seen.add(l)
        elif not l:
            if cleaned and cleaned[-1].strip():
                cleaned.append("")
    return "\n".join(cleaned).strip()
