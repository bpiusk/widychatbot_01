// Komponen login admin untuk autentikasi
import React, { useState } from "react";
import { adminLogin } from "../api";
import theme from "../theme";

export default function AdminLogin({ onLogin }) {
  // State untuk username, password, loading, dan error
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fungsi handle login admin
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await adminLogin(username, password);
      if (data.access_token) {
        onLogin(data.access_token);
      } else {
        setError("Username atau password salah.");
      }
    } catch {
      setError("Gagal login. Silakan coba lagi.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-white via-pink-100 to-purple-200 px-2 py-8">
      <div className="w-full max-w-md bg-white rounded-3xl border-2 border-purple-300 shadow-xl p-8 flex flex-col items-center gap-6">
        <div className="flex flex-col items-center gap-2">
          <span className="mb-2 flex justify-center items-center">
            <img
              src="/sparkle.png"
              alt="Logo"
              className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain"
            />
          </span>
          <h2 className="text-3xl font-extrabold text-purple-800 text-center drop-shadow">
            Login Admin
          </h2>
        </div>
        <form
          onSubmit={handleLogin}
          className="w-full flex flex-col gap-5 mt-2"
        >
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-purple-200 focus:outline-none focus:border-purple-500 bg-gray-50 text-gray-900 text-base shadow-sm transition"
            autoFocus
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-purple-200 focus:outline-none focus:border-purple-500 bg-gray-50 text-gray-900 text-base shadow-sm transition"
          />
          {error && (
            <div className="bg-red-100 text-red-700 border border-red-300 text-sm text-center font-medium rounded-lg py-2 px-3 animate-pulse">
              {error}
            </div>
          )}
          <button
            type="submit"
            className="bg-gradient-to-r from-purple-500 to-pink-400 hover:from-purple-600 hover:to-pink-500 text-white w-full font-bold py-3 rounded-xl shadow-lg transition disabled:opacity-50 text-lg"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  ></path>
                </svg>
                Loading...
              </span>
            ) : (
              "Login"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}