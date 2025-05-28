# 🎓 WidyChat - Chatbot Kampus Universitas Widya Dharma Pontianak

WidyChat adalah chatbot berbasis dokumen yang dapat menjawab pertanyaan tentang kampus Universitas Widya Dharma Pontianak. Chatbot ini dibangun menggunakan **LangChain**, **Streamlit**, **OpenAI API**, dan **ChromaDB**.

---

## 🚀 Fitur

- Menjawab pertanyaan tentang informasi umum kampus
- Mendukung percakapan dengan riwayat chat (chat memory)
- Bisa digunakan langsung via web browser (Streamlit)

---

## 🛠️ Struktur Proyek

📦project-root/
├── app.py
├── load_and_embed.py
├── chat_engine.py
├── .env
├── data/
│   └── [pdf-files]
├── vectorstore/
├── prompts/
│   └── rag_prompt.txt
└── utils/
    ├── pdf_reader.py
    └── splitter.py



---

## 📦 Persyaratan

- Python 3.9+
- Paket yang dibutuhkan:
  ```bash
  pip install -r requirements.txt

## 🧠 Cara Kerja
- Training Dokumen PDF
Jalankan script berikut untuk membaca semua PDF dalam folder data/ dan menyimpannya ke ChromaDB:
python load_and_embed.py

- Menjalankan Chatbot
Jalankan aplikasi Streamlit:
streamlit run app.py

- Tanya Jawab
Buka browser dan ajukan pertanyaan seperti:

"Apa saja fakultas yang tersedia?"

"Di mana alamat kampus?"

"Apakah ada fasilitas Wi-Fi?"

## 🧪 Tips
- Setiap kali kamu mengganti isi atau menambahkan PDF di folder data/, jalankan ulang:

python load_and_embed.py

- Jika ingin mengubah model embedding, sesuaikan di load_and_embed.py dan chat_engine.py.

## 🤝 Kontribusi
- Proyek ini terbuka untuk dikembangkan lebih lanjut, seperti:
Menambah fitur upload dokumen dari antarmuka
Menggunakan Pinecone atau Weaviate untuk skala besar
Menambahkan jawaban dengan sumber referensi dari dokumen

## 📬 Kontak
Untuk pertanyaan lebih lanjut, hubungi:

Email: info@widya.ac.id

Website: https://www.widya.ac.id

