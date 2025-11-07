from models.user import User
from models.post import Post
from models.forum import Forum
from models.membership import Membership
from models.message import Message   # 🟢 thêm dòng này trước configure_mappers
from models.like import Like 
from sqlalchemy.orm import configure_mappers
configure_mappers()  # chỉ an toàn khi tất cả model đã được import
