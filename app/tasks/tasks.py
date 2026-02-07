from app.models import AgentTask, Message
from celery import Celery
import asyncio
from app.agents.manager import AgentOrchestrator
from app.core.database import SessionLocal
from app.core.config import CONFIG
from app.enums import TaskStatus, MessageRole


celery = Celery(
    backend=CONFIG.REDIS_URL,
    broker=CONFIG.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery.task(bind=True)
def run_agent_task(self, prompt: str, user_id: str, message_id: str):
    with SessionLocal() as db:
        task = AgentTask(
            id=str(self.request.id),
            prompt=prompt,
            status=TaskStatus.RUNNING,
            user_id=user_id,
            message_id=message_id
        )
        db.add(task)
        db.commit()
        try:
            result = asyncio.run(AgentOrchestrator().run(prompt))
            task.status = TaskStatus.COMPLETED
            task.result = result
            new_message = Message(
                role=MessageRole.ASSISTANT,
                content=result,
                user_id=user_id
            )
            db.add(new_message)
            db.commit()
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = str(e)
            db.commit()
            return str(e)