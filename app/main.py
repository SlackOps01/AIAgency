from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response, RedirectResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from app.core.logging import logger
from app.core.limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.tasks.tasks import run_agent_task
from app.schemas.agent_task import AgentTaskRequest, AgentTaskResponse
from app.core.database import Base, engine
from app.models import *
from app.scripts import admin
from app.core.security import get_current_user
from app.schemas import TokenData
from app.api.v1.router import router as api_router
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.enums.messages import MessageRole
from redis.asyncio import Redis
from app.core.config import CONFIG






@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    Base.metadata.create_all(bind=engine)
    redis_client = Redis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, decode_responses=True)
    app.state.redis = redis_client
    admin.create_admin()
    try:
        try:
            await redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        yield
    except Exception as e:
        logger.error(e)
    finally:
        logger.info("Shutting down application...")




app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)


@app.get(
"/health",
description="Health check",
)
@limiter.limit("5/minute")
def health(request: Request):
    return {"status": "ok"}


@app.post("/run-agent", description="Run an agent")
@limiter.limit("5/minute")
def run_agent(request: Request, prompt: AgentTaskRequest, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    message = Message(
        role=MessageRole.USER,
        content=prompt.prompt,
        user_id=current_user.id
    )
    db.add(message)
    db.commit()
    task = run_agent_task.delay(prompt.prompt, current_user.id, message.id)
    return {"task_id": task.id}

@app.get("/tasks/{task_id}", response_model=AgentTaskResponse, description="Get task status")
@limiter.limit("5/minute")
def get_tasks(request: Request, task_id: str, current_user: TokenData = Depends(get_current_user)):
    result = run_agent_task.AsyncResult(task_id)
    return {"state": result.state, "result": result.result}


