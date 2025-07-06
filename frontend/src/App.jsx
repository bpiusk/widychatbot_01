// Komponen utama aplikasi React, mengatur routing dan autentikasi admin
import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Chatbot from "./components/Chatbot";
import AdminLogin from "./components/AdminLogin";
import AdminDashboard from "./components/AdminDashboard";
import AdminReport from "./components/AdminReport";

export default function App() {
  // State token admin
  const [adminToken, setAdminToken] = useState(localStorage.getItem("adminToken") || "");

  // Fungsi login admin
  const handleLogin = (token) => {
    setAdminToken(token);
    localStorage.setItem("adminToken", token);
  };

  // Fungsi logout admin
  const handleLogout = () => {
    setAdminToken("");
    localStorage.removeItem("adminToken");
  };

  // Routing aplikasi
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Chatbot />} />
        <Route
          path="/admin"
          element={
            adminToken ? (
              <Navigate to="/admin/dashboard" replace />
            ) : (
              <AdminLogin onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            adminToken ? (
              <AdminDashboard token={adminToken} onLogout={handleLogout} />
            ) : (
              <Navigate to="/admin" replace />
            )
          }
        />
        <Route
          path="/admin/reports"
          element={
            adminToken ? (
              <AdminReport token={adminToken} />
            ) : (
              <Navigate to="/admin" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}