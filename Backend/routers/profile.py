from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.post import Post   # 👈 Thêm import này
from datetime import datetime  # 👈 Thêm import
from pydantic import BaseModel # 👈 Thêm import
import os, shutil

router = APIRouter()

# 📁 Thư mục upload
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# 🟢 LẤY THÔNG TIN NGƯỜI DÙNG
# ============================================================
@router.get("/profile/{user_id}")
def get_profile(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    # Nếu có avatar, thêm base_url khi trả về
    base_url = str(request.base_url).rstrip("/")
    avatar_url = None
    if user.avatar:
        avatar_url = f"{base_url}/static/uploads/{user.avatar}"

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "avatar": avatar_url,  # Trả URL đầy đủ
        "background": user.background,
        "bio": user.bio
    }


# ============================================================
# 🟣 CẬP NHẬT ẢNH ĐẠI DIỆN (AVATAR)
# ============================================================
@router.post("/profile/update-avatar/{user_id}")
def update_avatar(
    request: Request,
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    # 🧩 Đảm bảo thư mục uploads tồn tại
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 🖼 Lưu file thật vào thư mục static/uploads
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 💾 Cập nhật DB — chỉ lưu tên file
    user.avatar = file.filename
    db.commit()
    db.refresh(user)

    return {
        "message": "Cập nhật avatar thành công",
        "file_name": file.filename
    }


# ============================================================
# 📦 SCHEMA TẠO STATUS
# ============================================================
class PostCreate(BaseModel):
    content: str


# ============================================================
# 🟢 ĐĂNG STATUS MỚI
# ============================================================
@router.post("/profile/{user_id}/post")
def create_status(user_id: int, post: PostCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    new_post = Post(
        user_id=user_id,
        content=post.content,
        created_at=datetime.utcnow()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "message": "Đăng status thành công",
        "post_id": new_post.post_id,
        "content": new_post.content,
        "created_at": new_post.created_at
    }


# ============================================================
# 🔵 LẤY DANH SÁCH STATUS CỦA NGƯỜI DÙNG
# ============================================================
@router.get("/profile/{user_id}/posts")
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .all()
    )

    return [
        {
            "post_id": p.post_id,
            "content": p.content,
            "created_at": p.created_at
        }
        for p in posts
    ]
@router.delete("/profile/post/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()  # ✅ dùng đúng tên cột
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")

    db.delete(post)
    db.commit()
    return {"message": "Xoá bài viết thành công"}
