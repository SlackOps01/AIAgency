from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, TEXT
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
from app.enums.messages import MessageRole
from uuid import uuid4

def get_now():
    return datetime.now(timezone.utc)

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(DateTime, default=get_now)

    # Relationships
    task = relationship("AgentTask", back_populates="message", uselist=False)
    user = relationship("User", back_populates="messages")
    generated_files = relationship("GeneratedFile", back_populates="message")