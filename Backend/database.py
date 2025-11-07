#fix lỗi hiển thị tiếng Việt
import sys
sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔧 Thay chuỗi URL bằng thông tin của bạn (Railway, PlanetScale hoặc localhost)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/forum_app"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
