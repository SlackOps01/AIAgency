from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime, timezone
from app.enums.users import UserRole
from app.enums.subscription import SubscriptionTier
from uuid import uuid4


def get_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_now)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)

    # Relationships
    tasks = relationship("AgentTask", back_populates="user")
    messages = relationship("Message", back_populates="user")
    generated_files = relationship("GeneratedFile", back_populates="user")