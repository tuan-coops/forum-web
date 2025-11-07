// ===============================
// 🔥 CẤU HÌNH FIREBASE CHO DỰ ÁN FORUMWEB-BDAFC
// ===============================

// ⚙️ Import Firebase SDK (nếu cần test trực tiếp trong file này)
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.5.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.5.0/firebase-analytics.js";

// 🚀 Cấu hình Firebase (bạn lấy từ Firebase Console)
export const firebaseConfig = {
  apiKey: "AIzaSyDT0J8cel6wJAgu54kjquk5iKVj6C6m4hA",
  authDomain: "forumweb-bdafc.firebaseapp.com",
  projectId: "forumweb-bdafc",
  storageBucket: "forumweb-bdafc.firebasestorage.app",
  messagingSenderId: "42592929051",
  appId: "1:42592929051:web:b35614c9b3f9a24b8dffbe",
  measurementId: "G-BHGJMYZY43"
};

// ✅ Khởi tạo Firebase (chỉ khi chạy độc lập)
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// ===============================
// 🌐 URL BACKEND API
// ===============================
// ⚠️ Nếu bạn chạy local thì dùng: http://127.0.0.1:8000
// ⚙️ Khi deploy thì đổi sang Render/Firebase Hosting endpoint của bạn.
export const API_BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"        // local backend
    : "https://forum-backend.onrender.com"; // Render backend



// Cho phép các file khác (login.js) truy cập biến toàn cục
window.API_BASE_URL = API_BASE_URL;
