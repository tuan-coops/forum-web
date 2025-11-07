from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from database import Base, engine
from routers.auth import router as auth_router
from routers.forum import router as forum_router
from routers.profile import router as profile_router
from routers import membership, message
from routers import chat  # thêm dòng này
import os

app = FastAPI(title="Forum API - FastAPI + MySQL")

# 🧭 Đường dẫn Frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../Frontend")
print("📂 Đường dẫn Frontend:", FRONTEND_DIR)

# 🟢 Mount thư mục Frontend & static
if os.path.exists(FRONTEND_DIR):
    app.mount("/Frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ⚙️ Cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🧠 Load toàn bộ models trước khi tạo bảng
import models

# 🧩 Tạo bảng nếu chưa có
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("⚠️ Không thể kết nối cơ sở dữ liệu:", e)


# 🔗 Gắn routers TRƯỚC redirect
app.include_router(auth_router)
app.include_router(forum_router)
app.include_router(profile_router)
app.include_router(membership.router)
app.include_router(message.router)
app.include_router(chat.router)  # thêm dòng này sau các router khác

print("✅ Routers đã được include thành công!")

# 🟣 Khi truy cập gốc '/', mở login-page
@app.get("/")
def open_login():
    login_path = os.path.join(FRONTEND_DIR, "home-page", "index.html")
    if not os.path.exists(login_path):
        return {"error": "Không tìm thấy file login-page/index.html"}
    return FileResponse(login_path)

# 🔁 Redirect CHỈ cho frontend
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
# ============================================================
# 📎 API UPLOAD FILE (TƯƠNG THÍCH VERCEL)
# ============================================================
from fastapi import UploadFile, File
import shutil

# 🔹 Đặt đường dẫn upload tương đối (tránh crash trên Vercel)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Nhận file tải lên và lưu vào thư mục uploads/"""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"url": f"/uploads/{file.filename}"}
    except Exception as e:
        return {"error": f"Không thể lưu file: {e}"}

# 🔹 Cho phép truy cập file qua URL
if os.path.exists(UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
else:
    print("⚠️ uploads directory not found, skip mounting")
