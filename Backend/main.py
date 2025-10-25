from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import Forum
from schemas import ForumCreate, ForumResponse
from typing import List

# Tạo bảng trong DB nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/forum/create", response_model=ForumResponse)
def create_forum(forum: ForumCreate, db: Session = Depends(get_db)):
    # Tạo forum mới
    new_forum = Forum(
        name=forum.name,
        description=forum.description,
        tag=forum.tag,
        avatar=forum.avatar,
        background=forum.background,
        created_by=forum.created_by,
    )

    db.add(new_forum)
    db.commit()
    db.refresh(new_forum)

    return new_forum

# 🟠 Cập nhật forum
@app.put("/forum/{forum_id}", response_model=ForumResponse)
def update_forum(forum_id: int, forum: ForumCreate, db: Session = Depends(get_db)):
    db_forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=404, detail="Forum not found")

    db_forum.name = forum.name
    db_forum.description = forum.description
    db_forum.tag = forum.tag
    db_forum.avatar = forum.avatar
    db_forum.background = forum.background

    db.commit()
    db.refresh(db_forum)
    return db_forum


# 🔵 Lấy tất cả forum
@app.get("/forum/", response_model=List[ForumResponse])
def get_forums(db: Session = Depends(get_db)):
    forums = db.query(Forum).all()
    return forums
# 🟡 Lấy forum theo ID
@app.get("/forum/{forum_id}", response_model=ForumResponse)
def get_forum_by_id(forum_id: int, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    return forum
# 🔴 Xóa forum
@app.delete("/forum/{forum_id}")
def delete_forum(forum_id: int, db: Session = Depends(get_db)):
    db_forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not db_forum:
        raise HTTPException(status_code=404, detail="Forum not found")

    db.delete(db_forum)
    db.commit()
    return {"message": f"Forum {forum_id} deleted successfully"}