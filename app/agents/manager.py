from app.agents.specialized_agents import LegalAgent, ManagerAgent, ResearchAgent
from app.agents.schemas.manager import LegalAgentRequest

class AgentOrchestrator:
    def __init__(self):
        self.manager_agent = ManagerAgent()
        self.legal_agent = LegalAgent()
        self.research_agent = ResearchAgent()
        self._setup_orchestrator()

    def _setup_orchestrator(self):
        # Register legal agent as a tool for the manager agent's inner pydantic agent
        self.legal_agent.register_as_tool(self.manager_agent.agent, LegalAgentRequest)
        self.research_agent.register_as_tool(self.manager_agent.agent)

    async def run(self, message: str):
        return await self.manager_agent.run(message)
