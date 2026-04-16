from fastapi import Depends, HTTPException, APIRouter

from app.agent.dto import AgentResponse, AgentRequest
from app.agent.service import AgentService
from app.deps import get_agent_service

router = APIRouter()


@router.post("/agent", response_model=AgentResponse, summary="질문 한 개만 받아서 에이전트 처리")
async def agent(
        req: AgentRequest,
        service: AgentService = Depends(get_agent_service),
):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    api_response = service.answer(question, req.image_keys)
    return api_response
