#splitter.py
# Utility functions to split raw text into structured chunks.
import re

def split_text(raw_text):
    """
    Memecah teks menjadi chunk berdasarkan blok:
    Pertanyaan: ...\nJawaban: ...\nTag: ...\n\n
    Robust terhadap spasi/baris kosong setelah Tag.
    """
    # Pola baru: lebih toleran terhadap spasi/baris kosong di antara label dan isi
    pattern = (
        r'(Pertanyaan:\s*.*?(?:\n(?!Pertanyaan:))*?'   # Pertanyaan: ... (boleh multiline, berhenti sebelum Pertanyaan: berikutnya)
        r'Jawaban:\s*.*?(?:\n(?!Pertanyaan:|Jawaban:))*?' # Jawaban: ... (boleh multiline, berhenti sebelum label berikutnya)
        r'Tag:\s*.*?(?:\n\s*\n|\n{2,}|$))'            # Tag: ... (boleh multiline, diakhiri baris kosong/ganda/akhir file)
    )
    chunks = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    # Jika hasil chunk <= 0, fallback ke chunk per N karakter
    if len(chunks) <= 0:
        N = 1200
        chunks = [raw_text[i:i+N] for i in range(0, len(raw_text), N) if raw_text[i:i+N].strip()]
        print(f"split_text fallback: Jumlah chunk dihasilkan = {len(chunks)}")
    else:
        print(f"split_text: Jumlah chunk dihasilkan = {len(chunks)}")
    return [chunk.strip() for chunk in chunks if chunk.strip()]
