from app.core.database import SessionLocal
from redis.asyncio import Redis
from fastapi import Request


def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()



async def get_redis(request: Request) -> Redis:
    return request.app.state.redis
