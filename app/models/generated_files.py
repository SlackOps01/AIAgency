from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
from app.enums.files import FileType
from uuid import uuid4

def get_now():
    return datetime.now(timezone.utc)

class GeneratedFile(Base):
    __tablename__ = "generated_files"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    task_id = Column(String, ForeignKey("agent_tasks.id"))
    user_id = Column(String, ForeignKey("users.id"))
    message_id = Column(String, ForeignKey("messages.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(Enum(FileType), default=FileType.PDF)
    file_size = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_now)

    # Relationships
    task = relationship("AgentTask", back_populates="generated_files")
    user = relationship("User", back_populates="generated_files")
    message = relationship("Message", back_populates="generated_files")
