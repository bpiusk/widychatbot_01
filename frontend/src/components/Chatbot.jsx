// Komponen utama Chatbot untuk UI dan logika chatbot kampus
import React, { useState, useRef, useEffect } from "react";
import { chat, sendFeedback } from "../api";

export default function Chatbot() {
  // State untuk menyimpan pesan chat
  const [messages, setMessages] = useState([]);
  // State untuk input user
  const [input, setInput] = useState("");
  // State untuk loading saat menunggu respon bot
  const [loading, setLoading] = useState(false);
  // State untuk menyimpan feedback like/dislike dan laporan
  const [feedback, setFeedback] = useState({}); // {idx: {type: "like"/"dislike", reported: bool}}
  const [showReport, setShowReport] = useState({}); // {idx: true/false}
  // Ref untuk scroll otomatis ke bawah
  const messagesEndRef = useRef(null);

  // Scroll ke bawah setiap kali pesan bertambah
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Fungsi kirim pesan
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Tambahkan pesan user ke chat
    const userMessage = { from: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Kirim pertanyaan ke API dan tunggu jawaban bot
      const response = await chat(input);
      const botMessage = { from: "bot", text: response.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      // Jika error, tampilkan pesan error dari bot
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "Terjadi kesalahan. Coba lagi." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Fungsi untuk mendeteksi dan merender list dari string jawaban bot
  function renderBotMessage(text) {
    // Deteksi list terurut (1. ... 2. ... dst)
    const lines = text.split("\n").map((line) => line.trim());
    const isNumberedList =
      lines.every((line) => /^\d+\./.test(line) || line === "" || line.length < 3) &&
      lines.filter((l) => l).length > 1;
    if (isNumberedList) {
      return (
        <ol className="list-decimal ml-6">
          {lines
            .filter((l) => l)
            .map((line, idx) => (
              <li key={idx}>{line.replace(/^\d+\.\s*/, "")}</li>
            ))}
        </ol>
      );
    }
    // Deteksi bullet list (- ... atau • ...)
    const isBulletList =
      lines.every((line) => /^[-•]/.test(line) || line === "" || line.length < 3) &&
      lines.filter((l) => l).length > 1;
    if (isBulletList) {
      return (
        <ul className="list-disc ml-6">
          {lines
            .filter((l) => l)
            .map((line, idx) => (
              <li key={idx}>{line.replace(/^[-•]\s*/, "")}</li>
            ))}
        </ul>
      );
    }
    // Default: tampilkan sebagai paragraf biasa
    return text.split("\n").map((line, idx) => (
      <span key={idx}>
        {line}
        <br />
      </span>
    ));
  }

  // Fungsi kirim feedback
  const handleFeedback = (idx, type) => {
    setFeedback((prev) => ({ ...prev, [idx]: { type, reported: false } }));
    setShowReport((prev) => ({ ...prev, [idx]: true }));
  };

  // Fungsi kirim laporan
  const handleReport = async (idx) => {
    const userMsgIdx = idx - 1;
    if (userMsgIdx < 0 || messages[userMsgIdx]?.from !== "user") return;
    const question = messages[userMsgIdx].text;
    const answer = messages[idx].text;
    const type = feedback[idx]?.type || "dislike";
    await sendFeedback(question, answer, type);
    setFeedback((prev) => ({ ...prev, [idx]: { ...prev[idx], reported: true } }));
    setShowReport((prev) => ({ ...prev, [idx]: false }));
    alert("Laporan telah dikirim ke admin.");
  };

  return (
    // Container utama chatbot
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-white via-pink-100 to-purple-100 text-[clamp(1.1rem,3vw,1.15rem)] px-0 sm:px-4 md:px-6">
      {/* Header: Judul dan logo chatbot */}
      <header className="w-full flex flex-col items-center pt-6 pb-3 text-[clamp(1.15rem,4vw,1.5rem)] font-light text-gray-800 font-[Manrope] text-center leading-tight">
        {/* SVG Sparkle Logo */}
        <span className="flex justify-center items-center mb-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="size-6"
          >
            <path
              fillRule="evenodd"
              d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5ZM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5ZM16.5 15a.75.75 0 0 1 .712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 0 1 0 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 0 1-1.422 0l-.395-1.183a1.5 1.5 0 0 0-.948-.948l-1.183-.395a.75.75 0 0 1 0-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0 1 16.5 15Z"
              clipRule="evenodd"
            />
          </svg>
        </span>
        Perlu info kampus? Tanya WidyChat saja!
      </header>
      {/* Chat Area: Menampilkan pesan chat */}
      <main className="flex-1 w-full flex justify-center overflow-y-auto pb-28">
        <div className="w-full max-w-full sm:max-w-3xl flex flex-col overflow-y-auto min-h-[60vh] px-0 sm:px-2">
          {/* Pesan awal jika belum ada chat */}
          {messages.length === 0 && !loading && (
            <div className="text-center text-gray-400 mt-10 select-none text-[clamp(1.1rem,3vw,1.15rem)]">
              Mulai percakapan dengan WidyChat...
            </div>
          )}

          <div className="flex flex-col gap-3 sm:gap-4">
            {/* Mapping pesan user dan bot */}
            {messages.map((msg, idx) => (
              <div key={idx}>
                <div
                  className={`flex ${
                    msg.from === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`w-full sm:w-auto px-4 py-2 sm:px-5 sm:py-3 max-w-full sm:max-w-[85%] rounded-2xl text-[clamp(1.1rem,3vw,1.15rem)] shadow-md break-words leading-relaxed backdrop-blur-md backdrop-saturate-150 ${
                      msg.from === "user"
                        ? "bg-white-200/30 text-gray-900 border border-white-300/20"
                        : "bg-purple-200/20 text-gray-900 border border-purple-300/20"
                    }`}
                    style={{
                      wordBreak: "break-word",
                      fontSize: "clamp(1.1rem, 3vw, 1.15rem)",
                    }}
                  >
                    {renderBotMessage(msg.text)}
                  </div>
                </div>
                {/* Tombol feedback hanya untuk pesan bot */}
                {msg.from === "bot" && (
                  <div className="flex gap-2 mt-1 ml-2">
                    {!feedback[idx]?.type && (
                      <>
                        <button
                          className="px-3 py-1 rounded-full bg-green-100 text-green-700 border border-green-300 hover:bg-green-200 text-xs"
                          onClick={() => handleFeedback(idx, "like")}
                        >
                          👍 Like
                        </button>
                        <button
                          className="px-3 py-1 rounded-full bg-red-100 text-red-700 border border-red-300 hover:bg-red-200 text-xs"
                          onClick={() => handleFeedback(idx, "dislike")}
                        >
                          👎 Dislike
                        </button>
                      </>
                    )}
                    {feedback[idx]?.type && !feedback[idx]?.reported && showReport[idx] && (
                      <button
                        className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-700 border border-yellow-300 hover:bg-yellow-200 text-xs"
                        onClick={() => handleReport(idx)}
                      >
                        Laporkan ke Admin
                      </button>
                    )}
                    {feedback[idx]?.reported && (
                      <span className="text-xs text-gray-500 ml-2">Laporan dikirim</span>
                    )}
                  </div>
                )}
              </div>
            ))}

            {/* Loading spinner saat bot mengetik */}
            {loading && (
              <div className="flex items-center gap-2 text-purple-500 text-sm">
                <span className="inline-block w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                <span>WidyChat sedang mengetik...</span>
              </div>
            )}

            {/* Ref untuk auto scroll ke bawah */}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </main>

      {/* Input Form: Form untuk mengetik dan mengirim pesan */}
      <form
        onSubmit={handleSend}
        className="w-full fixed bottom-3 left-0 flex justify-center px-0 sm:px-3 z-20"
        autoComplete="off"
      >
        <div className="w-full max-w-full sm:max-w-3xl flex items-center bg-white border border-gray-200 rounded-full shadow-lg px-3 sm:px-4 py-2 gap-2">
          <textarea
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              const el = e.target;
              el.style.height = "auto";
              el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
            }}
            placeholder="Tanyakan sesuatu tentang kampus..."
            disabled={loading}
            rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none text-[clamp(1.1rem,3vw,1.15rem)] px-2 sm:px-3 py-2 sm:py-3 overflow-y-auto max-h-[100px]"
            style={{
              fontSize: "clamp(1.1rem,3vw,1.15rem)",
              minHeight: "42px",
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-2 rounded-full text-purple-600 hover:bg-purple-50 transition disabled:opacity-50"
            aria-label="Kirim"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 12h14M12 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      </form>

      {/* Footer: Peringatan akurasi */}
      <footer className="fixed bottom-0 w-full text-center text-[clamp(0.95rem,2vw,1rem)] text-gray-500 py-1 bg-transparent z-10 backdrop-blur-sm">
        WidyChat tidak selalu akurat. Pastikan untuk memverifikasi informasi penting.
      </footer>
    </div>
  );
}
