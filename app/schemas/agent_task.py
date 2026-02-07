from pydantic import BaseModel, Field

class AgentTaskRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to run the agent with", examples=["What is the capital of France?"])


class AgentTaskResponse(BaseModel):
    state: str = Field(..., description="The state of the task", examples=["PENDING", "SUCCESS", "FAILURE"])
    result: str | None = Field(None, description="The result of the task")