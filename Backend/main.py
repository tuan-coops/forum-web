from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from database import Base, engine
from routers.auth import router as auth_router
from routers.forum import router as forum_router
from routers.profile import router as profile_router
from routers import membership, message, chat, tag
import os

app = FastAPI(title="Forum API - FastAPI + MySQL")

# ===============================
# 🧭 Đường dẫn Frontend
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../Frontend")
print("📂 FRONTEND_DIR:", FRONTEND_DIR)

if os.path.exists(FRONTEND_DIR):
    app.mount("/Frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ===============================
# ⚙️ Cấu hình CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# 🧠 Tạo bảng nếu có DB (bỏ qua nếu fail)
# ===============================
import models

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("⚠️ Database init failed:", e)

# ===============================
# 🔗 Routers
# ===============================
app.include_router(auth_router)
app.include_router(forum_router)
app.include_router(profile_router)
app.include_router(membership.router)
app.include_router(message.router)
app.include_router(chat.router)
app.include_router(tag.router) 

print("✅ Routers loaded successfully!")

# ===============================
# 🌐 Trang chủ → home-page
# ===============================
@app.get("/")
def open_home():
    login_path = os.path.join(FRONTEND_DIR, "home-page", "index.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "Không tìm thấy home-page"}

# ===============================
# 🔁 Redirect các thư mục frontend
# ===============================
@app.get("/{folder}/{path:path}")
def redirect_frontend(folder: str, path: str, request: Request):
    frontend_folders = {
        "home-page",
        "profile-page",
        "register-page",
        "create-forum-page",
        "search2-page"
    }

    if folder in frontend_folders:
        return RedirectResponse(url=f"/Frontend/{folder}/{path}")

    return {"detail": "Not Found"}

