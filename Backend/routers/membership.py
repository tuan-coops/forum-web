from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.membership import Membership
from schemas import MembershipBase, MembershipResponse
from datetime import datetime

router = APIRouter(
    prefix="/membership",
    tags=["Membership"]
)

# 🟢 1️⃣ Người dùng tham gia forum
@router.post("/join", response_model=MembershipResponse)
def join_forum(request: MembershipBase, db: Session = Depends(get_db)):
    existing = db.query(Membership).filter(
        Membership.user_id == request.user_id,
        Membership.forum_id == request.forum_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Người dùng đã tham gia forum này")

    new_member = Membership(
        user_id=request.user_id,
        forum_id=request.forum_id,
        role=request.role,
        joined_at=datetime.utcnow()
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


# 🧠 2️⃣ Xem tất cả thành viên trong 1 forum
@router.get("/{forum_id}", response_model=list[MembershipResponse])
def get_members(forum_id: int, db: Session = Depends(get_db)):
    return db.query(Membership).filter(Membership.forum_id == forum_id).all()


# 🟣 3️⃣ Lấy danh sách forum mà 1 user đã tham gia
@router.get("/user/{user_id}", response_model=list[MembershipResponse])
def get_forums_joined_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Membership).filter(Membership.user_id == user_id).all()


# 🔴 4️⃣ RỜI NHÓM (xoá membership)
@router.delete("/leave/{forum_id}/{user_id}")
def leave_forum(forum_id: int, user_id: int, db: Session = Depends(get_db)):
    membership = db.query(Membership).filter(
        Membership.forum_id == forum_id,
        Membership.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Người dùng không thuộc forum này")

    # 🚫 (tuỳ chọn) chặn admin rời nhóm:
    # if membership.role == "admin":
    #     raise HTTPException(status_code=400, detail="Admin không thể rời nhóm")

    db.delete(membership)
    db.commit()
    return {"message": "Đã rời nhóm thành công!"}
