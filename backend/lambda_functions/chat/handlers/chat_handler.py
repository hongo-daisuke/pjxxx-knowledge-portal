from __future__ import annotations

from aws_lambda_powertools.event_handler.api_gateway import Router

from services.chat_service import ChatService
from shared.auth import extract_claims
from shared.models import ChatRequest

router = Router()
_service = ChatService()


@router.post("/chat")
def ask() -> dict:
    claims = extract_claims(router.current_event.raw_event)
    req = ChatRequest.model_validate(router.current_event.json_body)
    response = _service.ask(req, claims)
    return response.model_dump()


# GET /chat/history は Phase 3 で追加予定
