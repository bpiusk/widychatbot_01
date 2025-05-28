import React, { useState, useEffect, useRef } from "react";
import { uploadPdf, listPdfs, deletePdf, reEmbed } from "../api";
import {
  Box,
  Button,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import { CloseIcon } from "@chakra-ui/icons";
import { useNavigate } from "react-router-dom";

export function ProgressBar({ progress }) {
  return (
    <div style={{ width: "100%", background: "#eee", borderRadius: 8, height: 12, marginBottom: 8 }}>
      <div
        style={{
          width: `${progress}%`,
          background: "#0d6efd",
          height: "100%",
          borderRadius: 8,
          transition: "width 0.3s",
        }}
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
  const logoutTimer = useRef(null);
  const fileInputRef = useRef();
  const navigate = useNavigate();

  // Cek token, jika tidak ada redirect ke login
  useEffect(() => {
    if (!token) {
      if (onLogout) onLogout();
      // Gunakan replace agar tidak bisa kembali ke dashboard dengan tombol back
      navigate("/admin/login", { replace: true });
    }
    // eslint-disable-next-line
  }, [token, navigate, onLogout]);

  // Fetch PDF list
  const fetchPdfs = async () => {
    try {
      const res = await listPdfs(token);
      // Pastikan hasilnya array, jika tidak jadikan array kosong
      setPdfs(Array.isArray(res) ? res : []);
    } catch {
      setPdfs([]); // fallback agar tidak error di .map()
      setMessage("Gagal mengambil daftar PDF.");
    }
  };

  useEffect(() => {
    fetchPdfs();
    // Auto logout after 30 minutes
    logoutTimer.current = setTimeout(() => {
      if (onLogout) onLogout();
      navigate("/admin/login", { replace: true });
    }, 30 * 60 * 1000);
    return () => clearTimeout(logoutTimer.current);
    // eslint-disable-next-line
  }, [navigate, onLogout]);

  // Polling progress
  useEffect(() => {
    let interval;
    if (embedLoading) {
      interval = setInterval(async () => {
        try {
          const res = await fetch("http://localhost:8000/admin/embed/progress");
          const data = await res.json();
          setEmbedProgress(data.progress || 0);
          if (data.status === "done" || data.progress >= 100) {
            setEmbedLoading(false);
            setEmbedProgress(100);
            setMessage("Embedding telah selesai.");
            fetchPdfs();
          }
        } catch {
          // error handling
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [embedLoading, token]);

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
    if (!window.confirm(`Hapus file ${filename}?`)) return;
    setMessage("");
    try {
      const res = await deletePdf(filename, token);
      setMessage(res.detail || "File dihapus.");
      fetchPdfs();
    } catch {
      setMessage("Gagal menghapus file.");
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

  return (
    <Box
      maxW="800px"
      w="100%"
      mx="auto"
      mt={10}
      p={6}
      borderRadius="xl"
      boxShadow="lg"
      bg="background.100"
      border="1px solid"
      borderColor="primary.500"
    >
      <Flex justify="space-between" align="center" mb={6}>
        <Text fontSize="2xl" fontWeight="bold" color="primary.500">
          Admin Dashboard
        </Text>
        <Button
          onClick={onLogout}
          colorScheme="secondary"
          bg="secondary.500"
          color="white"
          _hover={{ bg: "primary.500" }}
          size="sm"
        >
          Logout
        </Button>
      </Flex>

      {/* Info Aturan Upload */}
      <Flex align="flex-start" mb={6}>
        <Box fontSize={22} color="primary.500" mr={3} userSelect="none">
          ℹ️
        </Box>
        <Box fontSize={15} color="text.900">
          <b>Aturan upload file PDF:</b>
          <ul style={{ margin: "4px 0 0 18px", padding: 0 }}>
            <li>
              Nama file <b>tidak boleh mengandung spasi</b> atau karakter aneh (&amp;, %, #, dll).
            </li>
            <li>Ukuran file maksimal 10 MB.</li>
            <li>Format file harus <b>.pdf</b>.</li>
            <li>Pastikan isi dokumen jelas dan tidak rusak.</li>
            <li>
              Setelah upload, klik <b>Embedding Ulang</b> agar file bisa digunakan chatbot.
            </li>
          </ul>
        </Box>
      </Flex>

      {/* Upload PDF */}
      <form onSubmit={handleUpload}>
        <Flex mb={4} gap={2}>
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={e => setFile(e.target.files[0])}
            disabled={uploading || embedLoading}
          />
          <Button
            colorScheme="secondary"
            bg="secondary.500"
            color="white"
            _hover={{ bg: "accent.500" }}
            onClick={() => fileInputRef.current.click()}
            disabled={uploading || embedLoading}
          >
            Pilih File PDF
          </Button>
          <Text flex={1} color="primary.500" fontWeight="medium" isTruncated>
            {file ? file.name : "Belum ada file dipilih"}
          </Text>
          <Button
            type="submit"
            colorScheme="primary"
            bg="primary.500"
            color="white"
            _hover={{ bg: "accent.500" }}
            isLoading={uploading}
            disabled={uploading || !file || embedLoading}
          >
            Upload PDF
          </Button>
        </Flex>
        {uploading && <ProgressBar progress={progress} />}
      </form>

      {/* Embedding Ulang */}
      <Button
        onClick={handleEmbed}
        colorScheme="primary"
        bg="primary.500"
        color="white"
        _hover={{ bg: "accent.500" }}
        isLoading={embedLoading}
        mb={4}
        disabled={embedLoading}
      >
        {embedLoading ? "Memproses..." : "Embedding Ulang"}
      </Button>
      {embedLoading && (
        <Box my={3}>
          <ProgressBar progress={embedProgress} />
          <Text color="primary.500" fontWeight="medium">
            Embedding sedang diproses: {embedProgress}%
          </Text>
        </Box>
      )}

      {message && (
        <Box my={3} color="success.500" fontWeight="medium">
          {message}
        </Box>
      )}

      {/* Daftar PDF */}
      <Box mt={6}>
        <Text fontWeight="bold" color="primary.500" mb={2}>
          Daftar PDF
        </Text>
        <VStack align="stretch" spacing={2}>
          {/* Pastikan pdfs array sebelum map */}
          {(!Array.isArray(pdfs) || pdfs.length === 0) && (
            <Text color="text.700">Tidak ada file PDF.</Text>
          )}
          {Array.isArray(pdfs) && pdfs.map((pdf) => (
            <Flex
              key={pdf}
              align="center"
              justify="space-between"
              bg="white"
              borderRadius="md"
              px={4}
              py={2}
              border="1px solid"
              borderColor="primary.500"
            >
              <Text color="primary.500" fontWeight="medium">
                {pdf}
              </Text>
              <Button
                size="sm"
                colorScheme="red"
                variant="solid"
                onClick={() => handleDelete(pdf)}
                disabled={uploading || embedLoading}
              >
                Hapus
              </Button>
            </Flex>
          ))}
        </VStack>
      </Box>
    </Box>
  );
}