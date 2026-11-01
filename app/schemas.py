from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    model: str = "examate-fake"


class ChatResponse(BaseModel):
    answer: str


class UsageResponse(BaseModel):
    input_tokens: int
    output_tokens: int
    estimated: bool = False


class UsageSummary(BaseModel):
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: float