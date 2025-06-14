# test_cases.py

# Ini adalah daftar kasus uji untuk chatbot
TEST_CASES = [
    # --- Pertanyaan Normal (Dasar) ---
    {
        "question": "Berapa biaya kuliah Program Studi Manajemen S1 kelas pagi di Universitas Widya Dharma Pontianak?",
        "expected_answer": "Biaya kuliah Program Studi Manajemen S1 kelas pagi di UWDP terdiri dari SPP sebesar Rp 4.900.000, Dana Pembangunan dibagi menjadi dua tahap yaitu Rp 3.500.000 untuk DPP Tahap 1 dan Rp 4.150.000 untuk DPP Tahap 2. Total keseluruhan biaya adalah Rp 12.550.000."
    },
    {
        "question": "Apa saja syarat pendaftaran offline S1 di Universitas Widya Dharma Pontianak?",
        "expected_answer_keywords": ["fotokopi KTP", "fotokopi Kartu Keluarga", "rapor SLTA semester terakhir", "ijazah"]
    },
    {
        "question": "Di mana alamat Universitas Widya Dharma Pontianak?",
        "expected_answer": "Alamat Universitas Widya Dharma Pontianak berada di Jalan H.O.S. Cokroaminoto No. 445, Kota Pontianak, Kalimantan Barat 78117."
    },
    {
        "question": "Kapan jadwal pendaftaran Gelombang I Universitas Widya Dharma Pontianak Tahun Akademik 2025/2026?",
        "expected_answer": "Pendaftaran online Gelombang I Universitas Widya Dharma Pontianak untuk Tahun Akademik 2025/2026 dibuka mulai tanggal 7 April hingga 22 Mei 2025."
    },
    {
        "question": "Apakah biaya kuliah sudah termasuk asuransi kecelakaan?",
        "expected_answer": "Ya, biaya kuliah sudah termasuk asuransi kecelakaan. Cakupan asuransi ini melindungi mahasiswa selama kegiatan akademik di lingkungan kampus."
    },

    # --- Skenario Salah Input / Typo ---
    {
        "question": "Brapa biaya kuliah S1 Manajemen pagi?",
        "expected_answer_semantic": "Biaya kuliah Program Studi Manajemen S1 kelas pagi di UWDP adalah Rp 12.550.000." # Memeriksa pemahaman meskipun ada typo
    },
    {
        "question": "Syarat pendaftaran offline S1 UWDP apa sih?",
        "expected_answer_keywords": ["fotokopi KTP", "fotokopi Kartu Keluarga", "rapor SLTA semester terakhir", "ijazah"]
    },
    {
        "question": "Alamat UWDp dmn?",
        "expected_answer_contains": "Jalan H.O.S. Cokroaminoto No. 445, Pontianak."
    },
    {
        "question": "Kapan gelombang 1 buka?",
        "expected_answer_semantic": "Pendaftaran online Gelombang I Universitas Widya Dharma Pontianak untuk Tahun Akademik 2025/2026 dibuka mulai tanggal 7 April hingga 22 Mei 2025." # Memeriksa pemahaman query yang lebih singkat
    },
    {
        "question": "Apakah biaya kuliah termasuk asuransi?",
        "expected_answer_semantic": "Ya, biaya kuliah sudah termasuk asuransi kecelakaan." # Memeriksa pemahaman query yang lebih umum
    },
    {
        "question": "Info biaya S1 mandiri kelas pagi?", # Salah input jurusan (mandiri seharusnya mandarin)
        "expected_answer_semantic": "Biaya kuliah Program Studi Bahasa Mandarin S1 kelas pagi adalah Rp 12.550.000."
    },
    {
        "question": "Jam pendaftaran UWDP?", # Singkat dan ambigu
        "expected_answer_semantic": "Jam kerja bagian pendaftaran adalah setiap hari kerja, dari hari Senin hingga Sabtu, pukul 08.00 sampai 12.00 WIB."
    },
    {
        "question": "Nomor WA PMB S1?", # Singkat
        "expected_answer_contains": "0821 5220 7202."
    },
    {
        "question": "Ujian masuk berapa menit?", # Sangat singkat
        "expected_answer_semantic": "Durasi ujian saringan masuk online UWDP adalah selama 120 menit atau 2 jam tanpa jeda."
    },

    # --- Pertanyaan di Luar Konteks / Tidak Ada di Dokumen ---
    {
        "question": "Apakah UWDP memiliki program doktor?",
        "expected_answer_semantic": "Mohon maaf, informasi mengenai program doktor tidak ditemukan dalam dokumen yang saya miliki. Saya hanya dapat memberikan informasi berdasarkan dokumen yang tersedia." # Jawaban menolak atau menyatakan tidak ada informasi
    },
    {
        "question": "Bagaimana cara mendaftar beasiswa?",
        "expected_answer_semantic": "Mohon maaf, informasi mengenai cara mendaftar beasiswa tidak ditemukan dalam dokumen yang saya miliki."
    },
    {
        "question": "Siapa rektor Universitas Widya Dharma Pontianak?",
        "expected_answer_semantic": "Mohon maaf, informasi mengenai rektor Universitas Widya Dharma Pontianak tidak ditemukan dalam dokumen yang saya miliki."
    },
    {
        "question": "Berapa rata-rata IPK untuk masuk S1?",
        "expected_answer_semantic": "Mohon maaf, informasi mengenai rata-rata IPK untuk masuk S1 tidak ditemukan dalam dokumen yang saya miliki. Untuk S2, minimal IPK adalah 2.75." # Memberikan informasi terkait jika ada, dan menyatakan ketidaktersediaan info yang diminta
    },
    {
        "question": "Apakah UWDP memiliki asrama mahasiswa?",
        "expected_answer_semantic": "Mohon maaf, informasi mengenai fasilitas asrama mahasiswa tidak ditemukan dalam dokumen yang saya miliki."
    },

    # --- Pertanyaan Menggabungkan Informasi (Sulit) ---
    {
        "question": "Jika seorang calon mahasiswa mendaftar Program Studi Akuntansi (Transfer Non Alumni) kelas sore dan juga harus membayar biaya administrasi serta tabungan KTM, berapa total biaya keseluruhan yang harus mereka siapkan?",
        "expected_answer_semantic": "Total biaya kuliah untuk Program Studi Akuntansi (Transfer Non Alumni) kelas sore adalah Rp 13.350.000. Ditambah biaya administrasi Rp 300.000 dan tabungan KTM Rp 100.000, maka total keseluruhan biaya yang harus disiapkan adalah Rp 13.750.000."
    },
    {
        "question": "Bagaimana akreditasi S1 Sistem Informasi dibandingkan dengan S1 Informatika di UWDP?",
        "expected_answer_semantic": "Program Studi S1 Sistem Informasi terakreditasi Baik berdasarkan SK No. 6464/SK/BAN-PT/AK-PNB/S/X/2020 (BAN-PT), sedangkan Program Studi S1 Informatika terakreditasi Baik berdasarkan SK No. 047/SK/LAM-INFOKOM/AK/S/IV/2023 (LAM INFOKOM). Keduanya sama-sama berpredikat Baik."
    },
    {
        "question": "Saya ingin mendaftar S1 Manajemen kelas pagi. Jika saya bayar lunas pada 20 Februari 2025, berapa total biaya bersih yang harus saya keluarkan?",
        "expected_answer_semantic": "Biaya kuliah S1 Manajemen kelas pagi adalah Rp 12.550.000. Jika Anda membayar lunas pada 20 Februari 2025 (antara 1 Februari 2025 hingga 5 April 2025), Anda akan mendapatkan Cashback sebesar Rp 2.500.000. Jadi, total biaya bersih yang harus dikeluarkan adalah Rp 12.550.000 - Rp 2.500.000 = Rp 10.050.000."
    },
]