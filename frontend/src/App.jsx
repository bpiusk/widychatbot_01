import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Chatbot from "./components/Chatbot";
import AdminLogin from "./components/AdminLogin";
import AdminDashboard from "./components/AdminDashboard";

export default function App() {
  const [adminToken, setAdminToken] = useState(localStorage.getItem("adminToken") || "");

  const handleLogin = (token) => {
    setAdminToken(token);
    localStorage.setItem("adminToken", token);
  };

  const handleLogout = () => {
    setAdminToken("");
    localStorage.removeItem("adminToken");
  };

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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}