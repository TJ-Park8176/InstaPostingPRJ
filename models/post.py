from sqlalchemy import Column, Integer, String, Enum, Text, DateTime
from models.database import Base
import enum
import datetime

class PostStatus(enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    content_json = Column(Text) # Stores serialized CardNewsData
    caption = Column(Text)
    image_paths = Column(Text) # Comma separated paths
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

class InstagramConfig(Base):
    __tablename__ = "instagram_configs"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    business_account_id = Column(String)
