// Komponen utama Chatbot untuk UI dan logika chatbot kampus
import React, { useState, useRef, useEffect } from "react";
import { chat, sendFeedback } from "../api";
import theme from "../theme";

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
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-white via-pink-100 to-purple-200 text-[clamp(1.1rem,3vw,1.15rem)] px-0 sm:px-4 md:px-6">
      {/* Header: Judul dan logo chatbot */}
      <header className="w-full flex flex-col items-center pt-6 pb-3 text-[clamp(1.15rem,4vw,1.5rem)] font-light text-black-800 font-[Manrope] text-center leading-tight">
        <span className="flex justify-center items-center mb-2">
          <img
            src="/sparkle.png"
            alt="Logo"
            className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain"
          />
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
                    className={`
                      ${msg.from === "user"
                        ? "bg-white/80 text-gray-900 border border-purple-100"
                        : "bg-purple-200/60 text-black-900 border border-purple-200"}
                      rounded-2xl px-4 py-2 sm:px-5 sm:py-3
                      max-w-full sm:max-w-[85%]
                      shadow-md break-words leading-relaxed backdrop-blur-md backdrop-saturate-150
                      ${msg.from === "user" ? "ml-auto" : "mr-auto"}
                    `}
                    style={{
                      wordBreak: "break-word",
                      fontSize: "clamp(1.1rem, 3vw, 1.15rem)",
                    }}
                  >
                    {renderBotMessage(msg.text)}
                  </div>
                </div>
                {/* Tombol feedback hanya untuk pesan bot
                {msg.from === "bot" && (
                  <div className="flex gap-2 mt-1 ml-2">
                    {!feedback[idx]?.type && (
                      <>
                        <button
                          className={`px-3 py-1 rounded-full ${theme.feedbackLike} hover:bg-green-200 text-xs`}
                          onClick={() => handleFeedback(idx, "like")}
                        >
                          👍 Like
                        </button>
                        <button
                          className={`px-3 py-1 rounded-full ${theme.feedbackDislike} hover:bg-red-200 text-xs`}
                          onClick={() => handleFeedback(idx, "dislike")}
                        >
                          👎 Dislike
                        </button>
                      </>
                    )}
                    {feedback[idx]?.type && !feedback[idx]?.reported && showReport[idx] && (
                      <button
                        className={`px-3 py-1 rounded-full ${theme.feedbackReport} hover:bg-yellow-200 text-xs`}
                        onClick={() => handleReport(idx)}
                      >
                        Laporkan ke Admin
                      </button>
                    )}
                    {feedback[idx]?.reported && (
                      <span className="text-xs text-gray-500 ml-2">Laporan dikirim</span>
                    )}
                  </div>
                )} */}
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

      {/* Footer: Peringatan akurasi dan Input Form */}
      <div className="fixed bottom-0 left-0 w-full flex flex-col items-center pb-3 px-0 sm:px-3 z-20">
        {/* Input Form: Form untuk mengetik dan mengirim pesan */}
        <form
          onSubmit={handleSend}
          className="w-full max-w-full sm:max-w-3xl flex items-center bg-white border border-purple-200 rounded-full shadow-lg px-3 sm:px-4 py-2 gap-2"
          autoComplete="off"
        >
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
        </form>
        {/* Peringatan akurasi */}
        <footer className="w-full max-w-full sm:max-w-3xl text-center text-[clamp(0.95rem,2vw,1rem)] text-gray-500 py-1 bg-transparent backdrop-blur-sm">
          WidyChat tidak selalu akurat. Pastikan untuk memverifikasi informasi penting.
        </footer>
      </div>
    </div>
  );
}