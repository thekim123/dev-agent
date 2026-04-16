from __future__ import annotations

from fastapi import Request

from app.agent.service import AgentService


def get_image_storage(request: Request):
    return request.app.state.image_storage


def get_agent_service(request: Request) -> AgentService:
    return request.app.state.agent_service
