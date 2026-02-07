from pydantic import BaseModel, Field
from enum import Enum


class LegalAgentMode(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    COMPLIANCE = "compliance"
    RISK_ASSESSMENT = "risk_assessment"
    WRITE = "writing"


class LegalAgentRequest(BaseModel):
    mode: LegalAgentMode = Field(description="The mode of the legal agent.")
    prompt: str = Field(description="The prompt for the legal agent.")
    write_pdf: bool = Field(description="Whether to write the pdf.")
    