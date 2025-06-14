# test_chatbot.py

import requests
import os
import time

# Import pustaka NLP
import torch
from sentence_transformers import SentenceTransformer, util

# --- Import test_cases dari file terpisah ---
from test_cases import TEST_CASES

# --- Konfigurasi ---
BASE_URL = "http://127.0.0.1:8000"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

# --- Inisialisasi Model NLP (Dijalankan Sekali di Awal) ---
print("Memuat model SentenceTransformer untuk validasi semantik...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model SentenceTransformer berhasil dimuat.")
except Exception as e:
    print(f"Gagal memuat model SentenceTransformer: {e}")
    print("Validasi semantik tidak akan tersedia.")
    model = None


# --- Fungsi untuk Validasi Semantik ---
def semantic_similarity_check(actual_text, expected_text, threshold=0.7):
    if model is None:
        return False, 0.0
    if not actual_text or not expected_text:
        return False, 0.0
    try:
        embeddings1 = model.encode(actual_text, convert_to_tensor=True)
        embeddings2 = model.encode(expected_text, convert_to_tensor=True)
        cosine_sim = util.cos_sim(embeddings1, embeddings2).item()
        return cosine_sim >= threshold, cosine_sim
    except Exception as e:
        print(f"Error saat menghitung kemiripan semantik: {e}")
        return False, 0.0


# --- Fungsi Pengujian Utama ---
def run_chat_tests():
    passed_count = 0
    failed_count = 0
    total_response_time = 0.0 # Variabel baru untuk menjumlahkan waktu respons
    
    # Menggunakan TEST_CASES yang diimpor
    total_tests = len(TEST_CASES)

    print(f"Memulai pengujian chatbot di {CHAT_ENDPOINT}\n")

    # Menggunakan TEST_CASES yang diimpor
    for i, test_case in enumerate(TEST_CASES):
        question = test_case["question"]
        expected_answer = test_case.get("expected_answer")
        expected_keywords = test_case.get("expected_answer_keywords")
        expected_answer_contains = test_case.get("expected_answer_contains")
        expected_answer_semantic = test_case.get("expected_answer_semantic")

        print(f"--- Uji Kasus {i+1}/{total_tests} ---")
        print(f"Pertanyaan: '{question}'")

        actual_answer = ""
        response_time = 0.0 # Variabel untuk waktu respons per pertanyaan

        try:
            start_time = time.time() # Mulai mengukur waktu
            response = requests.post(CHAT_ENDPOINT, json={"question": question}, timeout=30)
            end_time = time.time() # Selesai mengukur waktu
            response_time = end_time - start_time
            total_response_time += response_time # Tambahkan ke total waktu

            response.raise_for_status()

            actual_response_data = response.json()
            actual_answer = actual_response_data.get("answer", "")

            print(f"Jawaban Aktual: '{actual_answer}'")
            print(f"Waktu Respons: {response_time:.2f} detik") # Tampilkan waktu respons

            is_passed = False
            reason = "Tidak ada kriteria validasi yang ditentukan untuk kasus uji ini."
            similarity_score_display = "N/A"

            # --- Logika Validasi ---
            if expected_answer:
                if actual_answer.strip().lower() == expected_answer.strip().lower():
                    is_passed = True
                    reason = "Jawaban sama persis."
                else:
                    reason = f"Jawaban tidak sama persis. Diharapkan: '{expected_answer}'"
                    if model:
                        _, sim_score = semantic_similarity_check(actual_answer, expected_answer, threshold=0)
                        similarity_score_display = f" (Similarity: {sim_score:.2f})"


            elif expected_keywords:
                all_keywords_found = all(keyword.lower() in actual_answer.lower() for keyword in expected_keywords)
                if all_keywords_found:
                    is_passed = True
                    reason = f"Semua keyword '{', '.join(expected_keywords)}' ditemukan."
                else:
                    missing_keywords = [k for k in expected_keywords if k.lower() not in actual_answer.lower()]
                    reason = f"Keyword tidak lengkap. Keyword hilang: '{', '.join(missing_keywords)}'."
                    if model and expected_keywords:
                            combined_expected_text = " ".join(expected_keywords)
                            _, sim_score = semantic_similarity_check(actual_answer, combined_expected_text, threshold=0)
                            similarity_score_display = f" (Similarity: {sim_score:.2f})"

            elif expected_answer_contains:
                if expected_answer_contains.lower() in actual_answer.lower():
                    is_passed = True
                    reason = f"Jawaban mengandung frasa: '{expected_answer_contains}'."
                else:
                    reason = f"Jawaban tidak mengandung frasa: '{expected_answer_contains}'."
                    if model:
                        _, sim_score = semantic_similarity_check(actual_answer, expected_answer_contains, threshold=0)
                        similarity_score_display = f" (Similarity: {sim_score:.2f})"

            elif expected_answer_semantic:
                if model is None:
                    reason = "Validasi semantik tidak bisa dilakukan: Model NLP tidak dimuat."
                    is_passed = False
                else:
                    passed_semantic, similarity_score = semantic_similarity_check(actual_answer, expected_answer_semantic)
                    similarity_score_display = f" (Similarity: {similarity_score:.2f})"
                    if passed_semantic:
                        is_passed = True
                        reason = f"Jawaban memiliki kemiripan semantik tinggi ({similarity_score:.2f}) dengan yang diharapkan."
                    else:
                        reason = f"Jawaban memiliki kemiripan semantik rendah ({similarity_score:.2f}) dengan yang diharapkan."

            if similarity_score_display != "N/A" and (expected_answer or expected_keywords or expected_answer_contains or expected_answer_semantic):
                print(f"Score Kemiripan: {similarity_score_display.strip()}")


            if is_passed:
                print("STATUS: LULUS ✅")
                passed_count += 1
            else:
                print(f"STATUS: GAGAL ❌ - {reason}")
                failed_count += 1

        except requests.exceptions.Timeout:
            print(f"Waktu Respons: {response_time:.2f} detik (Timeout)") # Tampilkan waktu respons jika timeout
            print("STATUS: GAGAL ❌ - Permintaan timeout (lebih dari 30 detik).")
            failed_count += 1
            # Jangan tambahkan response_time ke total_response_time jika timeout, karena itu bukan waktu respons yang sukses
        except requests.exceptions.ConnectionError:
            print(f"STATUS: GAGAL ❌ - Tidak dapat terhubung ke chatbot di {CHAT_ENDPOINT}. Pastikan server FastAPI berjalan.")
            failed_count += 1
        except requests.exceptions.RequestException as e:
            print(f"STATUS: GAGAL ❌ - Error saat membuat permintaan: {e}")
            failed_count += 1
        except Exception as e:
            print(f"STATUS: GAGAL ❌ - Error tak terduga: {e}")
            failed_count += 1
        print("-" * 50)

    print("\n=== Ringkasan Hasil Pengujian ===")
    print(f"Total Uji Kasus: {total_tests}")
    print(f"Lulus: {passed_count} ✅")
    print(f"Gagal: {failed_count} ❌")
    if total_tests > 0:
        print(f"Tingkat Kelulusan: {((passed_count / total_tests) * 100):.2f}%")
        # Hitung rata-rata waktu respons hanya untuk yang berhasil (tidak timeout)
        if passed_count + failed_count > 0: # Hanya jika ada percobaan
            average_response_time = total_response_time / (passed_count + failed_count)
            print(f"Rata-rata Waktu Respons (dari semua percobaan): {average_response_time:.2f} detik")
        else:
            print("Rata-rata Waktu Respons: N/A (Tidak ada percobaan)")
    else:
        print("Tingkat Kelulusan: N/A (Tidak ada kasus uji)")
        print("Rata-rata Waktu Respons: N/A (Tidak ada kasus uji)")

if __name__ == "__main__":
    run_chat_tests()