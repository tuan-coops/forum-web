from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from database import get_db
from models.membership import Membership, RoleEnum
from models.forum import Forum
from models.user import User
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
@router.get("/suggest")
def suggest_users(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.username.ilike(f"%{keyword}%"))
        .limit(8)
        .all()
    )
    return [{"user_id": u.user_id, "username": u.username} for u in users]

# 🧠 2️⃣ Xem tất cả thành viên trong 1 forum
@router.get("/{forum_id}")
def get_members(forum_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(Membership, User.username)
        .join(User, Membership.user_id == User.user_id)
        .filter(Membership.forum_id == forum_id)
        .all()
    )

    return [
        {
            "user_id": m.Membership.user_id,
            "username": m.username,
            "role": m.Membership.role,
            "joined_at": m.Membership.joined_at,
        }
        for m in results
    ]



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
@router.post("/add")
def add_member(
    forum_id: int = Body(...),
    username: str = Body(...),
    db: Session = Depends(get_db)
):
    # 🔹 Kiểm tra forum tồn tại
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum không tồn tại")

    # 🔹 Kiểm tra user tồn tại
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng này")

    # 🔹 Kiểm tra đã là thành viên chưa
    existing = db.query(Membership).filter(
        Membership.forum_id == forum_id,
        Membership.user_id == user.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Người dùng đã là thành viên của forum")

    # 🟢 Thêm mới
    new_member = Membership(user_id=user.user_id, forum_id=forum_id, role=RoleEnum.member)
    db.add(new_member)
    db.commit()

    return {"message": f"✅ Đã thêm {user.username} vào forum thành công!"}
@router.delete("/remove/{forum_id}/{target_user_id}")
def remove_member(
    forum_id: int,
    target_user_id: int,
    admin_id: int = Query(..., description="ID của admin thực hiện thao tác"),
    db: Session = Depends(get_db)
):
    """Xóa thành viên khỏi forum (chỉ admin được phép)"""
    # 🔹 Kiểm tra admin có trong nhóm không
    admin = db.query(Membership).filter(
        Membership.forum_id == forum_id,
        Membership.user_id == admin_id
    ).first()

    if not admin or admin.role != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa thành viên.")

    # 🔹 Kiểm tra user cần xóa có trong nhóm không
    member = db.query(Membership).filter(
        Membership.forum_id == forum_id,
        Membership.user_id == target_user_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Người dùng không thuộc forum này.")

    # 🚫 Chặn admin xóa chính mình
    if admin_id == target_user_id:
        raise HTTPException(status_code=400, detail="Không thể tự xóa chính mình.")

    # 🚫 Chặn admin xóa admin khác (nếu có nhiều admin)
    if member.role == RoleEnum.admin:
        raise HTTPException(status_code=400, detail="Không thể xóa một admin khác.")

    # ✅ Xóa thành viên
    db.delete(member)
    db.commit()
    return {"message": "✅ Thành viên đã bị xóa khỏi nhóm thành công!"}
