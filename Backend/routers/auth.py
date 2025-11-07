# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
import my_utils
from schemas import SignupRequest, SigninRequest, GoogleRegisterRequest
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials, auth

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔥 Khởi tạo Firebase chỉ 1 lần
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(os.getcwd(), "firebase-service-account.json"))
    firebase_admin.initialize_app(cred)


# 🧩 1️⃣ Đăng ký (MySQL)
@router.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == request.email).first()
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    if existing_username:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")

    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=my_utils.hash_password(request.password),
        avatar=request.avatar,
        background=request.background,
        bio=request.bio,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Đăng ký thành công"}


# 🧠 2️⃣ Đăng nhập tài khoản thường (MySQL)
@router.post("/signin")
def signin(request: SigninRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not my_utils.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")

    token = my_utils.create_token({
        "id": user.user_id,
        "email": user.email,
        "username": user.username
    })

    return {
        "token": token,
        "login_type": "mysql",
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "bio": user.bio
        }
    }


# 🔥 3️⃣ Đăng nhập Google qua Firebase
@router.post("/firebase-login")
async def firebase_login(request: Request, db: Session = Depends(get_db)):
    """
    Xác thực người dùng từ Firebase token:
    - Nếu email đã tồn tại → đăng nhập thành công
    - Nếu chưa có email → trả về need_register = True
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Body JSON không hợp lệ")

    id_token = body.get("idToken")
    if not id_token:
        raise HTTPException(status_code=400, detail="Thiếu Firebase ID token")

    # 🧩 Giải mã token Firebase
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email")
        name = decoded_token.get("name", email.split("@")[0] if email else "Người dùng")
        avatar = decoded_token.get("picture", "")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token Firebase không hợp lệ: {str(e)}")

    if not email:
        raise HTTPException(status_code=400, detail="Tài khoản Google không có email hợp lệ.")

    # 🔎 Kiểm tra user trong DB
    user = db.query(User).filter(User.email == email).first()

    if user:
        # ✅ Nếu user đã tồn tại → cho đăng nhập luôn
        if not user.firebase_uid:
            user.firebase_uid = uid
            db.commit()

        return {
            "need_register": False,
            "message": "Đăng nhập Firebase thành công",
            "login_type": "firebase",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar,
                "firebase_uid": user.firebase_uid
            }
        }

    # 🚨 Nếu chưa tồn tại user trong DB → yêu cầu đăng ký bổ sung
    return {
        "need_register": True,
        "email": email,
        "firebase_uid": uid,
        "avatar": avatar,
        "suggested_name": email.split("@")[0],
    }
@router.post("/register-from-google")
def register_from_google(request: GoogleRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email này đã có trong hệ thống")

    # ✅ Tạo user mới
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=my_utils.hash_password(request.password),
        avatar=request.avatar,
        firebase_uid=request.firebase_uid,
        bio=request.bio,
        created_at=datetime.utcnow()
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo tài khoản: {str(e)}")

    return {"message": "Đăng ký tài khoản Firebase thành công", "user_id": new_user.user_id}
