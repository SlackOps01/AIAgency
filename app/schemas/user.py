from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    subscription_tier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
