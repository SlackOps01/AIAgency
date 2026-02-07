import json
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import TokenData
from app.schemas.user import UserResponse
from app.core.security import get_current_user
from app.api.deps import get_db
from app.models.users import User
from app.scripts.hashing import verify_password
from app.core.security import create_access_token
from app.core.logging import logger
from app.core.limiter import limiter
from app.api.deps import get_redis
from redis.asyncio import Redis

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def me(request: Request, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db), redis: Redis = Depends(get_redis)):
    # Try to get cached user data from Redis
    cached_user = await redis.get(f"user:{current_user.id}")
    if cached_user:
        logger.info(f"cache hit")
        return UserResponse(**json.loads(cached_user))
    
    # Fetch from database
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert to response model and cache
    user_response = UserResponse.model_validate(user)
    logger.info(f"cache miss")
    await redis.set(f"user:{current_user.id}", user_response.model_dump_json(), ex=300)  # Cache for 5 minutes
    
    return user_response

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(data={"id": user.id, "role": user.role.value}), "token_type": "bearer"}


    