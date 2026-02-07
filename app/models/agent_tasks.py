from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
from app.enums.task_status import TaskStatus
from uuid import uuid4

def get_now():
    return datetime.now(timezone.utc)

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    prompt = Column(String, nullable=False)
    message_id = Column(String, ForeignKey("messages.id"))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)

    # Relationships
    message = relationship("Message", back_populates="task", foreign_keys=[message_id])
    generated_files = relationship("GeneratedFile", back_populates="task")
    user = relationship("User", back_populates="tasks")