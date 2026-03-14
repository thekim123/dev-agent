from pydantic import BaseModel, Field
from typing import List, Literal, Tuple

from app.ingestion.chunker import DocumentChunk


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class Source(BaseModel):
    path: str
    snippet: str | None = None
    line: int | None = None
    score: float | None = None


class AgentResponse(BaseModel):
    used_tool: Literal["retrieve_docs", "search_repo", "direct"]
    reason: str
    sources: List[Source]
    answer: str


class BedrockResponse(BaseModel):
    answer: str
    chunks: List[Tuple[float, DocumentChunk]]
