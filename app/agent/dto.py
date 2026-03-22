from typing import List, Literal

from pydantic import BaseModel, Field

from app.repository.base import ChunkSearchHit


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class Source(BaseModel):
    path: str
    snippet: str | None = None
    score: float | None = None


class AgentResponse(BaseModel):
    used_tool: Literal["retrieve_docs", "search_repo", "direct"]
    reason: str
    sources: List[Source]
    answer: str


class BedrockResponse(BaseModel):
    answer: str
    chunks: List[ChunkSearchHit]
