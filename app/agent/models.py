from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class RouteDecision:
    tool: Literal["direct", "search_repo", "retrieve_docs"]
    routed_question: str
    reason: str
    is_final: bool
    direct_answer: str | None = None
