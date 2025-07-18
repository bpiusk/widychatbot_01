// Komponen dashboard admin untuk mengelola file PDF dan proses embedding
import React, { useState, useEffect, useRef } from "react";
import { uploadPdf, listPdfs, deletePdf, reEmbed, deleteFileAndVector, listEmbeddedPdfs, deleteEmbeddedPdf } from "../api";
import { BASE_URL } from "../api";
import { useNavigate } from "react-router-dom";
import theme from "../theme";

// Komponen progress bar upload/embedding
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
  // State untuk daftar PDF, file yang diupload, status upload, dsb
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
  const [deletingFile, setDeletingFile] = useState(null); // File yang sedang dihapus
  const [deletingEmbeddedFile, setDeletingEmbeddedFile] = useState(null); // Embedded file yang sedang dihapus
  const navigate = useNavigate();

  // Cek token admin, redirect jika tidak ada
  useEffect(() => {
    if (!token) {
      if (onLogout) onLogout();
      window.location.replace("/admin/login");
    }
  }, [token, onLogout]);

  // Ambil daftar PDF dari server
  const fetchPdfs = async () => {
    try {
      const res = await listPdfs(token);
      setPdfs(Array.isArray(res) ? res : []);
    } catch {
      setPdfs([]);
      setMessage("Gagal mengambil daftar PDF.");
    }
  };

  // Ambil daftar PDF yang sudah di-embedding
  const fetchEmbeddedPdfs = async () => {
    try {
      const res = await listEmbeddedPdfs(token);
      setEmbeddedPdfs(Array.isArray(res) ? res : []);
    } catch {
      setEmbeddedPdfs([]);
    }
  };

  // Inisialisasi data dan timer logout otomatis
  useEffect(() => {
    fetchPdfs();
    fetchEmbeddedPdfs();
    logoutTimer.current = setTimeout(() => {
      if (onLogout) onLogout();
      window.location.replace("/admin/login");
    }, 30 * 60 * 1000);
    return () => clearTimeout(logoutTimer.current);
  }, [onLogout]);

  // Handle upload file PDF
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

  // Handle hapus file PDF & vektor
  const handleDelete = async (filename) => {
    if (!window.confirm(`Hapus file & vektor untuk ${filename}?`)) return;
    setMessage("");
    setDeletingFile(filename);
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
          fetchPdfs();
          setDeletingFile(null);
        }
      }, 700);
      fetchEmbeddedPdfs();
    } catch (err) {
      setMessage(err.message || "Gagal menghapus file & vektor.");
      setDeletingFile(null);
    }
  };

  // Handle hapus file embedded
  const handleDeleteEmbedded = async (filename) => {
    if (!window.confirm(`Hapus file embedded ${filename}?`)) return;
    setMessage("");
    setDeletingEmbeddedFile(filename);
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
          fetchEmbeddedPdfs();
          setDeletingEmbeddedFile(null);
        }
      }, 700);
      fetchPdfs();
    } catch (err) {
      setMessage(err.message || "Gagal menghapus embedded PDF.");
      setDeletingEmbeddedFile(null);
    }
  };

  // Handle proses embedding ulang
  const handleEmbed = async () => {
    setEmbedLoading(true);
    setEmbedProgress(0);
    setMessage("");
    try {
      const res = await reEmbed(token);
      setMessage(res.detail || "Embedding diproses.");
    } catch {
      setMessage("Gagal menjalankan embedding.");
      setEmbedLoading(false);
    }
  };

  // Polling progress embedding dari backend
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
    <div className={`min-h-screen w-full flex flex-col items-center justify-start bg-gradient-to-b from-white via-pink-100 to-purple-200 py-8 px-2`}>
      <div className={`w-full max-w-3xl mx-auto ${theme.adminBackground} ${theme.cardShadow} rounded-3xl ${theme.cardBorder} p-6 md:p-10 flex flex-col gap-6`}>
        {/* Header */}
        <div className="flex flex-col items-center gap-2 mb-2">
          {/* Ganti SVG dengan gambar */}
          <span className="mb-2 flex justify-center items-center">
            <img
              src="/sparkle.png" // atau "/logo/wd.jpg" atau "/stars.png"
              alt="Logo"
              className="w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20 object-contain"
            />
          </span>
          <span className="text-3xl md:text-4xl font-extrabold text-purple-800 text-center drop-shadow">Dashboard Admin</span>
        </div>
        {/* Tombol ke halaman laporan feedback */}
        <div className="flex justify-end mb-2">
          {/* <button
            onClick={() => {
              navigate("/admin/reports");
            }}
            className={`${theme.buttonSecondary} font-semibold py-2 px-6 rounded-xl shadow transition text-base mr-2`
          >
            Lihat Laporan Feedback
          </button> */}
          <button
            onClick={() => {
              if (window.confirm("Apakah Anda yakin ingin logout?")) {
                if (onLogout) {
                  onLogout();
                }
                window.location.replace("/admin/login");
              }
            }}
            className={`${theme.buttonPrimary} font-semibold py-2 px-6 rounded-xl shadow transition text-base focus:outline-none focus:ring-2 focus:ring-purple-300`}
          >
            Logout
          </button>
        </div>
        {/* Info Section */}
        <div className={`${theme.infoSection} rounded-xl p-4 shadow-sm flex items-start gap-3`}>
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
            className={`${theme.buttonSecondary} font-bold px-5 py-2 rounded-xl shadow transition disabled:opacity-60`}
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
            className={`${theme.buttonPrimary} font-bold px-5 py-2 rounded-xl shadow transition disabled:opacity-60`}
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
          {embedLoading ? "Memproses..." : "Embedding"}
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
          <span className={`${theme.textPrimary} font-bold mb-2 block text-lg`}>Daftar PDF</span>
          <div className="flex flex-col gap-2">
            {(!Array.isArray(pdfs) || pdfs.length === 0) && (
              <span className={theme.textSecondary}>Tidak ada file PDF.</span>
            )}
            {Array.isArray(pdfs) && pdfs.map((pdf) => (
              <div
                key={pdf}
                className={`flex items-center justify-between bg-white rounded-lg px-4 py-2 ${theme.cardBorder} shadow-sm hover:shadow-md transition`}
              >
                <span className={`${theme.textPrimary} font-medium truncate flex items-center gap-2`}>
                  <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                  {pdf}
                </span>
                <button
                  className={`${theme.buttonDanger} px-3 py-1 rounded-lg shadow text-sm transition disabled:opacity-60 disabled:cursor-not-allowed`}
                  onClick={() => handleDelete(pdf)}
                  disabled={
                    uploading ||
                    embedLoading ||
                    deletingFile !== null // Disable semua tombol hapus saat ada file yang sedang dihapus
                  }
                >
                  {deletingFile === pdf ? "Menghapus..." : "Hapus"}
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
              <span className={theme.textSecondary}>Tidak ada file embedded.</span>
            )}
            {Array.isArray(embeddedPdfs) && embeddedPdfs.map((pdf) => (
              <div
                key={pdf}
                className={`${theme.embeddedBubble} flex items-center justify-between rounded-lg px-4 py-2 shadow-sm hover:shadow-md transition`}
              >
                <span className="font-medium truncate flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                  {pdf}
                </span>
                <button
                  className={`${theme.buttonOutlineDanger} px-3 py-1 rounded-lg text-sm shadow transition disabled:opacity-60 disabled:cursor-not-allowed`}
                  onClick={() => handleDeleteEmbedded(pdf)}
                  disabled={uploading || embedLoading || deletingEmbeddedFile === pdf}
                >
                  {deletingEmbeddedFile === pdf ? "Menghapus..." : "Hapus"}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}