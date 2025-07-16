import React, { useEffect, useState } from "react";
import { getFeedbackReports } from "../api";
import { useNavigate } from "react-router-dom";
import theme from "../theme";

const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";

// Tambahkan fungsi hapus laporan
async function deleteFeedbackReport(id, token) {
  const res = await fetch(`${BASE_URL}/admin/reports/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Gagal menghapus laporan");
  return res.json();
}

export default function AdminReport({ token }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getFeedbackReports(token).then((data) => {
      setReports(data || []);
      setLoading(false);
    });
  }, [token]);

  const handleDelete = async (id) => {
    if (!window.confirm("Hapus laporan ini?")) return;
    setDeletingId(id);
    try {
      await deleteFeedbackReport(id, token);
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch {
      alert("Gagal menghapus laporan.");
    }
    setDeletingId(null);
  };

  return (
    <div className={`min-h-screen flex flex-col items-center ${theme.background} py-8 px-2`}>
      <div className={`w-full max-w-3xl ${theme.adminBackground} ${theme.cardShadow} rounded-3xl ${theme.cardBorder} p-8 flex flex-col gap-6`}>
        {/* Logo diambil dari theme.logoSvg */}
        <div className="flex justify-center mb-2">
          <span
            dangerouslySetInnerHTML={{ __html: theme.logoSvg }}
            aria-label="Logo"
          />
        </div>
        <div className="flex justify-end mb-2">
          <button
            onClick={() => navigate("/admin/dashboard")}
            className={`${theme.buttonPrimary} font-semibold py-2 px-6 rounded-xl shadow transition text-base`}
          >
            Kembali ke Dashboard
          </button>
        </div>
        <h2 className={`${theme.textPrimary} text-2xl font-bold mb-4`}>Laporan Feedback Chatbot</h2>
        {loading ? (
          <div>Loading...</div>
        ) : reports.length === 0 ? (
          <div className={theme.textMuted}>Belum ada laporan.</div>
        ) : (
          <div className="flex flex-col gap-4">
            {reports.map((r, idx) => (
              <div key={r.id || idx} className="bg-gray-50 border border-gray-200 rounded-xl p-4 shadow">
                <div className="mb-2">
                  <span className={`${theme.textPrimary} font-semibold`}>Pertanyaan:</span>
                  <div className={theme.textSecondary}>{r.question}</div>
                </div>
                <div className="mb-2">
                  <span className={`${theme.textPrimary} font-semibold`}>Jawaban:</span>
                  <div className={theme.textSecondary}>{r.answer}</div>
                </div>
                <div className="flex gap-4 items-center">
                  <span className={`${theme.textPrimary} font-semibold`}>Feedback:</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    r.feedback_type === "like"
                      ? theme.feedbackLike
                      : theme.feedbackDislike
                  }`}>
                    {r.feedback_type === "like" ? "Like 👍" : "Dislike 👎"}
                  </span>
                  <span className="ml-auto text-xs text-gray-500">{new Date(r.reported_at).toLocaleString()}</span>
                  <button
                    className={`ml-4 px-3 py-1 rounded-full ${theme.buttonOutlineDanger} hover:bg-red-200 text-xs`}
                    onClick={() => handleDelete(r.id)}
                    disabled={deletingId === r.id}
                  >
                    {deletingId === r.id ? "Menghapus..." : "Hapus"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
