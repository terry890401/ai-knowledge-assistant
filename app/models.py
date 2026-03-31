from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc)) #每次新增資料才執行，每筆資料有自己的時間

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), default = "新對話")
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="conversation")
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False) # user 或 assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default = lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")