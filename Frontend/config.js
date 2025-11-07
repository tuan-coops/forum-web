// 🧭 Tự động chọn API_BASE_URL
const API_BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"        // local backend
    : "https://forum-backend.onrender.com"; // Render backend

console.log("🔗 API_BASE_URL =", API_BASE_URL);
