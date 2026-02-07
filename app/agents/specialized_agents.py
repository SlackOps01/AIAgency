from pathlib import Path
from app.agents.base import SubAgent
from app.agents.tools.pdf_tool import write_pdf
from app.agents.tools.search_tool import robust_search_tool
from datetime import datetime, timezone
import json
from pathlib import Path



config_path = Path(__file__).parent.parent.parent / "config" / "config.json"

with open(config_path, "r") as f:
    config = json.load(f)

legal_agent_config = config["legal_agent"]
manager_agent_config = config["manager_agent"]
research_agent_config = config["research_agent"]

def date_tool():
    return datetime.now(timezone.utc).isoformat()


def load_prompt(prompt_name: str) -> str:
    """Load a system prompt from the prompts directory."""
    # Assuming app/prompts is adjacent to app/agents (i.e. ../prompts from here)
    prompt_path = Path(__file__).parent.parent / "prompts" / f"{prompt_name}.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        # Fallback or error handling
        print(f"Warning: Prompt file {prompt_path} not found.")
        return ""


class LegalAgent(SubAgent):
    def __init__(self):
        super().__init__(
            name="Legal Agent",
            model_name=legal_agent_config["model"],
            system_prompt=load_prompt("legal_agent"),
            tools=[write_pdf, date_tool],
            description="Handle legal matters, contracts, compliance, and regulatory frameworks."
        )

class ManagerAgent(SubAgent):
    def __init__(self):
        super().__init__(
            name="Manager Agent",
            model_name=manager_agent_config["model"],
            system_prompt=load_prompt("manager_agent"),
            description="Handle overall project management, task delegation, strategic planning, and quality assurance."
        )

class ResearchAgent(SubAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            model_name=research_agent_config["model"],
            system_prompt=load_prompt("research_agent"),
            tools=[robust_search_tool(), date_tool],
            description="Conduct research, gather information, and synthesize findings from web searches."
        )