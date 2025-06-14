import React, { useState, useEffect, useRef } from "react";
import { uploadPdf, listPdfs, deletePdf, reEmbed, deleteFileAndVector, listEmbeddedPdfs, deleteEmbeddedPdf } from "../api";
import { BASE_URL } from "../api";

export function ProgressBar({ progress }) {
  return (
    <div className="w-full bg-gray-200 rounded h-3 mb-2">
      <div
        className="bg-blue-600 h-full rounded transition-all"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

export default function AdminDashboard({ token, onLogout }) {
  const [pdfs, setPdfs] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [embedLoading, setEmbedLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const [embedProgress, setEmbedProgress] = useState(0);
  const [embeddedPdfs, setEmbeddedPdfs] = useState([]);
  const logoutTimer = useRef(null);
  const fileInputRef = useRef();
  const [deletingFile, setDeletingFile] = useState(null); // Tambahkan state ini
  const [deletingEmbeddedFile, setDeletingEmbeddedFile] = useState(null); // Tambahkan state ini untuk embedded

  useEffect(() => {
    if (!token) {
      if (onLogout) onLogout();
      window.location.replace("/admin/login");
    }
  }, [token, onLogout]);

  const fetchPdfs = async () => {
    try {
      const res = await listPdfs(token);
      setPdfs(Array.isArray(res) ? res : []);
    } catch {
      setPdfs([]);
      setMessage("Gagal mengambil daftar PDF.");
    }
  };

  const fetchEmbeddedPdfs = async () => {
    try {
      const res = await listEmbeddedPdfs(token);
      setEmbeddedPdfs(Array.isArray(res) ? res : []);
    } catch {
      setEmbeddedPdfs([]);
    }
  };

  useEffect(() => {
    fetchPdfs();
    fetchEmbeddedPdfs();
    logoutTimer.current = setTimeout(() => {
      if (onLogout) onLogout();
      window.location.replace("/admin/login");
    }, 30 * 60 * 1000);
    return () => clearTimeout(logoutTimer.current);
  }, [onLogout]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || embedLoading) return;
    setUploading(true);
    setMessage("");
    setProgress(0);
    try {
      const res = await uploadPdf(file, token, (prog) => setProgress(prog));
      setMessage(res.detail || "Upload berhasil.");
      setFile(null);
      fetchPdfs();
    } catch {
      setMessage("Gagal upload PDF.");
    }
    setUploading(false);
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Hapus file & vektor untuk ${filename}?`)) return;
    setMessage("");
    setDeletingFile(filename); // Set file yang sedang dihapus
    try {
      const res = await deleteFileAndVector(filename, token);
      setMessage(res.detail || "File & vektor dihapus.");
      let tries = 0;
      const poll = setInterval(async () => {
        const latest = await listPdfs(token);
        setPdfs(Array.isArray(latest) ? latest : []);
        tries++;
        if (!latest.includes(filename) || tries > 7) {
          clearInterval(poll);
          fetchPdfs(); // pastikan state terbaru
          setDeletingFile(null); // Reset setelah selesai
        }
      }, 700);
      fetchEmbeddedPdfs();
    } catch (err) {
      setMessage(err.message || "Gagal menghapus file & vektor.");
      setDeletingFile(null); // Reset jika gagal
    }
  };

  const handleDeleteEmbedded = async (filename) => {
    if (!window.confirm(`Hapus file embedded ${filename}?`)) return;
    setMessage("");
    setDeletingEmbeddedFile(filename); // Set file embedded yang sedang dihapus
    try {
      const res = await deleteEmbeddedPdf(filename, token);
      setMessage(res.detail || "Embedded PDF dihapus.");
      let tries = 0;
      const poll = setInterval(async () => {
        const latest = await listEmbeddedPdfs(token);
        setEmbeddedPdfs(Array.isArray(latest) ? latest : []);
        tries++;
        if (!latest.includes(filename) || tries > 7) {
          clearInterval(poll);
          fetchEmbeddedPdfs(); // pastikan state terbaru
          setDeletingEmbeddedFile(null); // Reset setelah selesai
        }
      }, 700);
      fetchPdfs();
    } catch (err) {
      setMessage(err.message || "Gagal menghapus embedded PDF.");
      setDeletingEmbeddedFile(null); // Reset jika gagal
    }
  };

  const handleEmbed = async () => {
    setEmbedLoading(true);
    setEmbedProgress(0);
    setMessage("");
    try {
      const res = await reEmbed(token);
      setMessage(res.detail || "Embedding ulang diproses.");
    } catch {
      setMessage("Gagal menjalankan embedding ulang.");
      setEmbedLoading(false);
    }
  };

  // Tambahkan polling progress embedding dengan BASE_URL
  useEffect(() => {
    let interval;
    if (embedLoading) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${BASE_URL}/admin/embed/progress`);
          const data = await res.json();
          setEmbedProgress(data.progress || 0);
          if (data.status === "done") {
            setEmbedLoading(false);
            setTimeout(() => {
              fetchEmbeddedPdfs();
              fetchPdfs();
            }, 500);
            clearInterval(interval);
          }
        } catch {}
      }, 1200);
    }
    return () => clearInterval(interval);
  }, [embedLoading]);

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-start bg-gradient-to-b from-purple-100 via-pink-100 to-white py-8 px-2">
      <div className="w-full max-w-3xl mx-auto bg-white/90 shadow-2xl rounded-3xl border border-purple-300 p-6 md:p-10 flex flex-col gap-6">
        {/* Header */}
        <div className="flex flex-col items-center gap-2 mb-2">
          <span className="text-purple-700 text-4xl md:text-5xl mb-1">★</span>
          <span className="text-3xl md:text-4xl font-extrabold text-purple-800 text-center drop-shadow">Admin Dashboard</span>
        </div>
        {/* Logout Button (always visible, right top) */}
        <div className="flex justify-end mb-2">
          <button
            onClick={() => { // <--- Tambahkan fungsi anonim di sini
              if (window.confirm("Apakah Anda yakin ingin logout?")) {
                if (onLogout) {
                  onLogout();
                }
                window.location.replace("/admin/login");
              }
            }}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-2 px-6 rounded-xl shadow hover:from-purple-600 hover:to-pink-600 transition text-base focus:outline-none focus:ring-2 focus:ring-purple-300"
          >
            Logout
          </button>
        </div>
        {/* Info Section */}
        <div className="flex items-start gap-3 bg-purple-50 border border-purple-200 rounded-xl p-4 shadow-sm">
          <span className="text-3xl text-purple-600 select-none">ℹ️</span>
          <div className="text-base text-gray-900">
            <b>Aturan upload file PDF:</b>
            <ul className="list-disc ml-5 mt-1 space-y-1 text-sm md:text-base">
              <li>Nama file <b>tidak boleh mengandung spasi</b> atau karakter aneh (&, %, #, dll).</li>
              <li>Ukuran file maksimal 10 MB.</li>
              <li>Format file harus <b>.pdf</b>.</li>
              <li>Pastikan isi dokumen jelas dan tidak rusak.</li>
              <li>Setelah upload, klik <b>Embedding Ulang</b> agar file bisa digunakan chatbot.</li>
            </ul>
          </div>
        </div>
        {/* Upload Form */}
        <form onSubmit={handleUpload} className="flex flex-col md:flex-row gap-3 items-center mb-2">
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={e => setFile(e.target.files[0])}
            disabled={uploading || embedLoading}
          />
          <button
            type="button"
            className="bg-yellow-400 hover:bg-yellow-500 text-white font-bold px-5 py-2 rounded-xl shadow transition disabled:opacity-60"
            onClick={() => fileInputRef.current.click()}
            disabled={uploading || embedLoading}
          >
            Pilih File PDF
          </button>
          <span className="flex-1 text-purple-700 font-medium truncate text-center md:text-left">
            {file ? file.name : "Belum ada file dipilih"}
          </span>
          <button
            type="submit"
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold px-5 py-2 rounded-xl shadow transition disabled:opacity-60"
            disabled={uploading || !file || embedLoading}
          >
            {uploading ? "Uploading..." : "Upload PDF"}
          </button>
        </form>
        {uploading && <ProgressBar progress={progress} />}
        {/* Embedding Button */}
        <button
          onClick={handleEmbed}
          className="bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 rounded-xl shadow-lg hover:from-pink-600 hover:to-purple-700 transition mb-2 w-full text-lg disabled:opacity-60"
          disabled={embedLoading || pdfs.length === 0}
        >
          {embedLoading ? "Memproses..." : "Embedding Ulang"}
        </button>
        {embedLoading && (
          <div className="my-3">
            <ProgressBar progress={embedProgress} />
            <span className="text-purple-700 font-medium">Embedding sedang diproses: {embedProgress}%</span>
          </div>
        )}
        {message && <div className="my-3 text-green-600 font-semibold text-center">{message}</div>}
        {/* Daftar PDF */}
        <div className="mt-2">
          <span className="font-bold text-purple-700 mb-2 block text-lg">Daftar PDF</span>
          <div className="flex flex-col gap-2">
            {(!Array.isArray(pdfs) || pdfs.length === 0) && (
              <span className="text-gray-700">Tidak ada file PDF.</span>
            )}
            {Array.isArray(pdfs) && pdfs.map((pdf) => (
              <div
                key={pdf}
                className="flex items-center justify-between bg-white rounded-lg px-4 py-2 border border-purple-200 shadow-sm hover:shadow-md transition"
              >
                <span className="text-purple-700 font-medium truncate flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                  {pdf}
                </span>
               <button
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg shadow text-sm transition disabled:opacity-60 disabled:cursor-not-allowed" // Tambahkan disabled style
                  onClick={() => handleDelete(pdf)}
                  disabled={uploading || embedLoading || deletingFile === pdf} // Tambahkan kondisi disabled
                >
                  {deletingFile === pdf ? "Menghapus..." : "Hapus"} {/* Ubah teks */}
                </button>
              </div>
            ))}
          </div>
        </div>
        {/* Daftar Embedded PDF */}
        <div className="mt-2">
          <span className="font-bold text-green-600 mb-2 block text-lg">Daftar PDF yang sudah di-embedding</span>
          <div className="flex flex-col gap-2">
            {(!Array.isArray(embeddedPdfs) || embeddedPdfs.length === 0) && (
              <span className="text-gray-700">Tidak ada file embedded.</span>
            )}
            {Array.isArray(embeddedPdfs) && embeddedPdfs.map((pdf) => (
              <div
                key={pdf}
                className="flex items-center justify-between bg-green-50 rounded-lg px-4 py-2 border border-green-300 shadow-sm hover:shadow-md transition"
              >
                <span className="text-green-700 font-medium truncate flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                  {pdf}
                </span>
                <button
                  className="border border-red-500 text-red-500 px-3 py-1 rounded-lg hover:bg-red-100 text-sm shadow transition disabled:opacity-60 disabled:cursor-not-allowed" // Tambahkan disabled style
                  onClick={() => handleDeleteEmbedded(pdf)}
                  disabled={uploading || embedLoading || deletingEmbeddedFile === pdf} // Tambahkan kondisi disabled
                >
                  {deletingEmbeddedFile === pdf ? "Menghapus..." : "Hapus"} {/* Ubah teks */}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}