import React, { useState, useRef, useEffect } from "react";
import { chat } from "../api";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { from: "user", text: input }]);
    setLoading(true);
    try {
      const res = await chat(input);
      setMessages((prev) => [...prev, { from: "bot", text: res.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "Terjadi kesalahan. Coba lagi." },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-white via-pink-100 to-purple-100">
      {/* Header */}
      <header className="w-full flex flex-col items-center pt-8 pb-4 px-4">
        <span className="text-purple-400 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="size-6">
            <path fillRule="evenodd" d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5ZM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5ZM16.5 15a.75.75 0 0 1 .712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 0 1 0 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 0 1-1.422 0l-.395-1.183a1.5 1.5 0 0 0-.948-.948l-1.183-.395a.75.75 0 0 1 0-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0 1 16.5 15Z" clipRule="evenodd" />
          </svg>
        </span>
        <h1 className="text-2xl md:text-3xl font-light text-gray-900 text-center font-[Manrope]">
          Need campus info? Just ask WidyChat
        </h1>
      </header>

      {/* Chat Area */}
      <main className="flex-1 w-full flex justify-center">
        <div className="w-full max-w-2xl flex flex-col px-4 md:px-0">
          <div className="flex-1 flex flex-col gap-4 overflow-y-auto pb-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-10 select-none">
                Mulai percakapan dengan WidyChat...
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex w-full ${
                  msg.from === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-4 py-3 max-w-[80%] rounded-2xl text-base shadow-md break-words ${
                    msg.from === "user"
                      ? "bg-white text-gray-900 border border-gray-200"
                      : "bg-purple-50 text-gray-900 border border-purple-200"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-purple-500 text-sm">
                <span className="inline-block w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></span>
                <span>WidyChat sedang mengetik...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full text-center text-xs text-gray-500 py-2 bg-transparent">
        WidyChat tidak selalu akurat. Pastikan untuk memverifikasi informasi penting.
      </footer>

      {/* Input Bar */}
      <form
        onSubmit={handleSend}
        className="w-full fixed bottom-0 left-0 flex justify-center bg-transparent px-2 py-3 sm:px-4"
        autoComplete="off"
      >
        <div className="w-full max-w-2xl flex items-center bg-white border border-gray-200 rounded-full shadow-lg px-4 py-2 gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanyakan sesuatu tentang kampus..."
            disabled={loading}
            className="flex-1 bg-transparent border-none outline-none text-base px-2 py-2"
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
    </div>
  );
}
