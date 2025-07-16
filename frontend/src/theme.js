// Semua warna utama aplikasi didefinisikan di sini.
// Ubah nilai di bawah untuk mengubah warna global aplikasi.

const theme = {
  // Warna latar belakang utama aplikasi (chatbot & admin)
  background: "bg-gradient-to-b from-purple-100 via-pink-50 to-white",

  // Warna bubble chat user & bot
  bubbleUser: "bg-white/80 text-gray-900 border border-purple-100",
  bubbleBot: "bg-pink-200/60 text-purple-900 border border-pink-200",

  // Warna tombol utama (gradasi ungu-pink)
  buttonPrimary: "bg-gradient-to-r from-purple-500 to-pink-400 hover:from-purple-600 hover:to-pink-500 text-white",
  buttonSecondary: "bg-yellow-400 hover:bg-yellow-500 text-white",
  buttonDanger: "bg-pink-400 hover:bg-pink-500 text-white",
  buttonOutlineDanger: "border border-red-500 text-red-500 hover:bg-red-100",

  // Warna feedback (like/dislike)
  feedbackLike: "bg-green-100 text-green-700 border border-green-300",
  feedbackDislike: "bg-red-100 text-red-700 border border-red-300",
  feedbackReport: "bg-yellow-100 text-yellow-700 border border-yellow-300",

  // Warna progress bar
  progressBar: "bg-blue-600",

  // Warna border dan shadow
  cardBorder: "border-purple-300",
  cardShadow: "shadow-2xl",

  // Warna teks utama
  textPrimary: "text-purple-800",
  textSecondary: "text-gray-900",
  textMuted: "text-gray-500",

  // Warna latar dashboard/admin
  adminBackground: "bg-white",

  // Warna bubble embedded PDF
  embeddedBubble: "bg-green-50 border border-green-300 text-green-700",

  // Warna info section (biru muda)
  infoSection: "bg-blue-50 border border-blue-200",

  // Footer
  footer: "text-gray-500 bg-transparent",
};

export default theme;
