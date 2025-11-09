from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import get_db
from models.forum import Forum
from datetime import datetime
from schemas import ForumCreate
import shutil, os
from models.membership import Membership, RoleEnum
from models.user import User
from models.like import Like
from models.message import Message
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/forum",
    tags=["Forum"]
)

# 🟢 Tạo forum mới
@router.post("/create")
def create_forum(
    request: Request,
    name: str = Form(...),
    tag: str = Form(...),
    caption: str = Form(""),
    created_by: int = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_path = None

    # 🖼 Nếu có ảnh thì lưu file, chỉ lưu phần sau static/
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path = f"uploads/{file.filename}"  # chỉ lưu phần sau static/

    # 🧱 Tạo forum mới
    new_forum = Forum(
        name=name,
        tag=tag,
        caption=caption,
        background=image_path,
        created_by=created_by
    )
    db.add(new_forum)
    db.commit()
    db.refresh(new_forum)

    # 👑 Thêm người tạo vào membership với quyền admin
    creator_membership = Membership(
        user_id=created_by,
        forum_id=new_forum.forum_id,
        role=RoleEnum.admin
    )
    db.add(creator_membership)
    db.commit()

    return {
        "message": "Tạo forum thành công",
        "forum_id": new_forum.forum_id,
        "role": "admin",
        "saved_path": image_path
    }


# 🟢 Lấy danh sách forum có phân trang
@router.get("/page")
def get_forum_list(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    base_url = str(request.base_url).rstrip("/")

    forums = (
        db.query(
            Forum,
            func.count(func.distinct(Membership.user_id)).label("member_count"),
            func.count(func.distinct(Like.like_id)).label("like_count")
        )
        .outerjoin(Membership, Membership.forum_id == Forum.forum_id)
        .outerjoin(Like, Like.forum_id == Forum.forum_id)
        .group_by(Forum.forum_id)
        .order_by(Forum.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = db.query(func.count(Forum.forum_id)).scalar()

    results = []
    for f, member_count, like_count in forums:
        bg_url = f"{base_url}/static/{f.background}" if f.background else None
        results.append({
            "forum_id": f.forum_id,
            "name": f.name,
            "tag": f.tag,
            "caption": f.caption,
            "background": bg_url,
            "created_by": f.created_by,
            "created_at": f.created_at,
            "member_count": member_count or 0,
            "like_count": like_count or 0,
        })

    return {"page": page, "limit": limit, "total": total, "results": results}


# 🟣 Trending forums
@router.get("/trending")
def get_trending_forums(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    base_url = str(request.base_url).rstrip("/")
    offset = (page - 1) * limit

    forums = (
        db.query(
            Forum.forum_id,
            Forum.name,
            Forum.caption,
            Forum.background,
            Forum.tag,
            Forum.created_by,
            Forum.created_at
        )
        .order_by(Forum.created_at.desc())  # 🟢 giữ nguyên thứ tự mới nhất
        .offset(offset)  # 🟢 phân trang thực sự
        .limit(limit)
        .all()
    )

    total = db.query(func.count(Forum.forum_id)).scalar()

    trending_list = [
        {
            "forum_id": f.forum_id,
            "name": f.name,
            "caption": f.caption,
            "background": f"{base_url}/static/{f.background}" if f.background else None,
            "tag": f.tag,
            "created_by": f.created_by,
            "created_at": f.created_at
        }
        for f in forums
    ]

    return {"page": page, "limit": limit, "total": total, "results": trending_list}


# 🔍 Tìm kiếm forum theo từ khóa
@router.get("/search")
def search_forums(request: Request, keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    forums = db.query(Forum).filter(
        or_(
            Forum.name.ilike(f"%{keyword}%"),
            Forum.tag.ilike(f"%{keyword}%"),
            Forum.caption.ilike(f"%{keyword}%")
        )
    ).all()

    base_url = str(request.base_url).rstrip("/")
    return {
        "results": [
            {
                "forum_id": f.forum_id,
                "name": f.name,
                "tag": f.tag,
                "caption": f.caption,
                "background": f"{base_url}/static/{f.background}" if f.background else None,
                "created_by": f.created_by,
                "created_at": f.created_at
            }
            for f in forums
        ]
    }
# 🟣 Lấy danh sách forum theo tag, xếp theo số thành viên & lượt like
@router.get("/by-tag/{tag_name}")
def get_forums_by_tag(
    tag_name: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Trả về danh sách forum có tag được chỉ định (tag lưu trực tiếp trong bảng forum),
    sắp xếp theo member_count và like_count giảm dần
    """
    base_url = str(request.base_url).rstrip("/")

    forums = (
        db.query(
            Forum,
            func.count(func.distinct(Membership.user_id)).label("member_count"),
            func.count(func.distinct(Like.like_id)).label("like_count")
        )
        .outerjoin(Membership, Membership.forum_id == Forum.forum_id)
        .outerjoin(Like, Like.forum_id == Forum.forum_id)
        .filter(func.lower(Forum.tag) == func.lower(tag_name))
        .group_by(Forum.forum_id)
        .order_by(func.count(func.distinct(Membership.user_id)).desc(),
                  func.count(func.distinct(Like.like_id)).desc())
        .all()
    )

    if not forums:
        raise HTTPException(status_code=404, detail=f"Không có forum nào với tag '{tag_name}'")

    results = []
    for f, member_count, like_count in forums:
        bg_url = f"{base_url}/static/{f.background}" if f.background else None
        results.append({
            "forum_id": f.forum_id,
            "name": f.name,
            "tag": f.tag,
            "caption": f.caption,
            "background": bg_url,
            "created_by": f.created_by,
            "created_at": f.created_at,
            "member_count": member_count or 0,
            "like_count": like_count or 0
        })

    return {
        "tag": tag_name,
        "total": len(results),
        "results": results
    }

# 🔵 Lấy tất cả forums
@router.get("/")
def get_all_forums(request: Request, db: Session = Depends(get_db)):
    forums = db.query(Forum).all()
    base_url = str(request.base_url).rstrip("/")
    return [
        {
            "forum_id": f.forum_id,
            "name": f.name,
            "tag": f.tag,
            "caption": f.caption,
            "background": f"{base_url}/static/{f.background}" if f.background else None,
            "created_by": f.created_by,
            "created_at": f.created_at
        }
        for f in forums
    ]


# 🔵 Forums user đã tham gia
@router.get("/joined/{user_id}")
def get_joined_forums(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Lấy danh sách forum mà user đã tham gia,
    kèm số lượng thành viên, tin nhắn, và hoạt động gần nhất.
    """
    joined_forums = (
        db.query(Forum)
        .join(Membership, Forum.forum_id == Membership.forum_id)
        .filter(Membership.user_id == user_id)
        .all()
    )

    base_url = str(request.base_url).rstrip("/")
    results = []

    for f in joined_forums:
        # ✅ Đếm thành viên
        member_count = (
            db.query(func.count(Membership.user_id))
            .filter(Membership.forum_id == f.forum_id)
            .scalar()
        )

        # ✅ Đếm tin nhắn
        try:
            message_count = (
                db.query(func.count(Message.message_id))
                .filter(Message.forum_id == f.forum_id)
                .scalar()
            )
        except Exception:
            message_count = 0

        # ✅ Lấy tin nhắn gần nhất + username
        last_msg = (
            db.query(Message, User.username)
            .join(User, Message.user_id == User.user_id)
            .filter(Message.forum_id == f.forum_id)
            .order_by(Message.created_at.desc())
            .first()
        )

        if last_msg:
            msg, username = last_msg
            last_activity = {
                "user": username,
                "time": msg.created_at
            }
        else:
            last_activity = None

        # ✅ Gộp kết quả
        results.append({
            "forum_id": f.forum_id,
            "name": f.name,
            "tag": f.tag,
            "caption": f.caption,
            "background": f"{base_url}/static/{f.background}" if f.background else None,
            "created_by": f.created_by,
            "created_at": f.created_at,
            "member_count": member_count,
            "message_count": message_count,
            "last_activity": last_activity
        })

    return results

# 🟠 Forums user đã tạo
@router.get("/created/{user_id}")
def get_forums_created_by_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    from models.like import Like     # import bảng Like nếu có
    from models.membership import Membership

    forums = db.query(Forum).filter(Forum.created_by == user_id).all()
    base_url = str(request.base_url).rstrip("/")

    result = []
    for f in forums:
        like_count = db.query(Like).filter(Like.forum_id == f.forum_id).count()
        member_count = db.query(Membership).filter(Membership.forum_id == f.forum_id).count()

        result.append({
            "forum_id": f.forum_id,
            "name": f.name,
            "tag": f.tag,
            "caption": f.caption,
            "background": f"{base_url}/static/{f.background}" if f.background else None,
            "created_at": f.created_at,
            "like_count": like_count,
            "member_count": member_count
        })
    return result



# 🟣 Lấy forum theo ID (kèm like_count & member_count)
@router.get("/{forum_id}")
def get_forum_by_id(request: Request, forum_id: int, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/")

    # 🔹 Dùng join để đếm like và member (tương tự get_forum_list)
    query = (
        db.query(
            Forum,
            func.count(func.distinct(Membership.user_id)).label("member_count"),
            func.count(func.distinct(Like.like_id)).label("like_count")
        )
        .outerjoin(Membership, Membership.forum_id == Forum.forum_id)
        .outerjoin(Like, Like.forum_id == Forum.forum_id)
        .filter(Forum.forum_id == forum_id)
        .group_by(Forum.forum_id)
    )

    result = query.first()

    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy forum")

    forum, member_count, like_count = result

    bg_url = f"{base_url}/static/{forum.background}" if forum.background else None

    return {
        "forum_id": forum.forum_id,
        "name": forum.name,
        "tag": forum.tag,
        "caption": forum.caption,
        "background": bg_url,
        "created_by": forum.created_by,
        "created_at": forum.created_at,
        "member_count": member_count or 0,
        "like_count": like_count or 0
    }


# 🔴 Xóa forum
@router.delete("/{forum_id}")
def delete_forum(forum_id: int, db: Session = Depends(get_db)):
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Không tìm thấy forum")
    db.delete(forum)
    db.commit()
    return {"message": "Xóa forum thành công"}
# 🟣 Cập nhật thông tin forum (tên, caption, tag, background)
@router.put("/update/{forum_id}")
def update_forum(
    forum_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Không tìm thấy forum")

    name = data.get("name")
    tag = data.get("tag")
    caption = data.get("caption")

    if name:
        forum.name = name
    if tag:
        forum.tag = tag
    if caption:
        forum.caption = caption

    forum.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(forum)

    return {"message": "✅ Cập nhật forum thành công", "forum": forum.name}
# 🟢 Lấy danh sách thành viên trong forum
@router.get("/members/{forum_id}")
def get_forum_members(forum_id: int, db: Session = Depends(get_db)):
    memberships = (
        db.query(Membership, User)
        .join(User, Membership.user_id == User.user_id)
        .filter(Membership.forum_id == forum_id)
        .all()
    )

    if not memberships:
        raise HTTPException(status_code=404, detail="Không có thành viên nào trong forum")

    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "role": m.role.value
        }
        for m, u in memberships
    ]
# 🖼️ Cập nhật ảnh đại diện (background) của forum
@router.put("/update-bg/{forum_id}")
def update_forum_background(
    forum_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Không tìm thấy forum")

    # 🧱 Tạo thư mục upload nếu chưa có
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 🔄 Lưu file mới
    filename = f"forum_{forum_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🧹 Xóa ảnh cũ (nếu có)
    if forum.background and os.path.exists(os.path.join("static", forum.background)):
        try:
            os.remove(os.path.join("static", forum.background))
        except Exception as e:
            print(f"⚠️ Không thể xóa ảnh cũ: {e}")

    # 🟢 Lưu đường dẫn mới vào DB (chỉ lưu phần sau static/)
    forum.background = f"uploads/{filename}"
    forum.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(forum)

    return {
        "message": "✅ Cập nhật ảnh forum thành công",
        "new_background_url": f"/static/uploads/{filename}"
    }
# ❤️ Like / Unlike forum
@router.post("/{forum_id}/like")
def toggle_like(
    forum_id: int,
    user_id: int = Query(..., description="ID của người dùng thực hiện hành động"),
    db: Session = Depends(get_db)
):
    forum = db.query(Forum).filter(Forum.forum_id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Không tìm thấy forum")

    existing_like = db.query(Like).filter(
        Like.forum_id == forum_id,
        Like.user_id == user_id
    ).first()

    # Nếu user đã like rồi => bỏ like
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"liked": False, "message": "Đã bỏ thích"}

    # Nếu chưa => thêm like
    new_like = Like(forum_id=forum_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    return {"liked": True, "message": "Đã thích"}
# ❤️ Lấy danh sách forum mà user đã like
@router.get("/liked/{user_id}")
def get_liked_forums(user_id: int, db: Session = Depends(get_db)):
    liked_forums = db.query(Like.forum_id).filter(Like.user_id == user_id).all()
    return {"liked_forum_ids": [f.forum_id for f in liked_forums]}
@router.post("/upload")
async def upload_forum_image(file: UploadFile = File(...)):
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/static/uploads/{file.filename}"}
