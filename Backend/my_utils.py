# utils.py
from passlib.context import CryptContext #băm và ktra mk
from jose import jwt #tạo và giải mã token
from datetime import datetime, timedelta #xử lý thời gian

SECRET_KEY = "YOUR_SECRET_KEY" 
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str): #plain: mk nhập vào, hashed: mk đã băm lưu trong db
    return pwd_context.verify(plain, hashed)

def create_token(data: dict): #
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
