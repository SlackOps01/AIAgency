import asyncio
from app.core.config import CONFIG
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic import BaseModel 
from typing import Union, Type, Optional
from app.core.logging import logger
from pydantic_ai.models.openrouter import OpenRouterModelSettings
 
class BaseAgent:

    def __init__(self, name: str, model_name: str, system_prompt: str, tools: list = None, description: str = None):
        self.name = name
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.tools = tools
        self.description = description
        self.agent = self._setup_agent()
        self.a2a = self.agent.to_a2a()


    def _setup_agent(self) -> Agent:
        model = OpenRouterModel(
            model_name=self.model_name,
            provider=OpenRouterProvider(
                api_key=CONFIG.OPENROUTER_API_KEY
            ),
            settings=OpenRouterModelSettings(
                temperature=0.1,
                top_p=0.1,
                extra_body={
                    "reasoning": {
                        "effort": "high",
                        "exclude": True
                  }
                }
            )
        )
        return Agent(model=model, tools=self.tools or [], system_prompt=self.system_prompt, retries=2)
        

    async def run(self, message: str, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                response = await self.agent.run(message)
                return response.output
            except UnexpectedModelBehavior as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.error(f"[{self.name}] OpenRouter error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"[{self.name}] Failed after {max_retries} attempts: {e}")
                    raise


class SubAgent(BaseAgent):
    def register_as_tool(self, parent: Agent, input_schema: Optional[Type[BaseModel]] = None):
        tool_name = f"ask_{self.name.lower().replace(' ', '_')}"

        if input_schema:
            async def call_sub_agent(args: input_schema):
                try:
                    response = await self.run(str(args.model_dump()))
                    return response
                except Exception as e:
                    return str(e)

            call_sub_agent.__annotations__['args'] = input_schema
        
        else:
            async def call_sub_agent(messages: str):
                try:
                    response = await self.run(messages)
                    logger.info(f"[{self.name}] Subagent response: {response[:50]}...")
                    return response
                except Exception as e:
                    logger.error(f"[{self.name}] Subagent error: {e}")
                    return str(e)

        call_sub_agent.__name__ = tool_name
        call_sub_agent.__doc__ = self.description

        parent.tool_plain(call_sub_agent)
        return call_sub_agent
        