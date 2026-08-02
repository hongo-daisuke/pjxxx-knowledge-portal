from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from infrastructure.bedrock_handler import BedrockHandler
from repositories.chat_repository import ChatRepository
from shared.kb_filter import build_retrieval_filter
from shared.models import ChatRequest, ChatResponse, Citation, UserClaims

_NO_HIT_MESSAGE = (
    "お探しの情報に該当する社内文書が見つかりませんでした。"
    "別のキーワードで質問するか、文書が Knowledge Base に同期されているかご確認ください。"
)


class ChatService:
    def __init__(
        self,
        bedrock: BedrockHandler | None = None,
        chat_repo: ChatRepository | None = None,
    ) -> None:
        self._bedrock = bedrock or BedrockHandler()
        self._repo = chat_repo or ChatRepository()

    def ask(self, req: ChatRequest, claims: UserClaims) -> ChatResponse:
        start = time.monotonic()

        filter_expression = build_retrieval_filter(claims)
        chunks = self._bedrock.retrieve(req.question, filter_expression)

        if not chunks:
            return ChatResponse(answer=None, no_hit=True)

        answer_text = self._bedrock.converse(req.question, chunks)

        citations = [
            Citation(
                doc_id=_extract_doc_id(chunk),
                title=_extract_title(chunk),
                score=float(chunk.get("score", 0.0)),
                s3_uri=chunk.get("location", {}).get("s3Location", {}).get("uri", ""),
            )
            for chunk in chunks
        ]

        latency_ms = int((time.monotonic() - start) * 1000)
        now = datetime.now(timezone.utc).isoformat()

        self._repo.save_history({
            "user_id": claims.sub,
            "timestamp": now,
            "question": req.question,
            "answer": answer_text,
            "citations": [c.model_dump() for c in citations],
            "latency_ms": latency_ms,
        })

        return ChatResponse(answer=answer_text, citations=citations)

    def list_history(self, claims: UserClaims) -> list[dict[str, Any]]:
        result = self._repo.list_history(user_id=claims.sub)
        return result.get("Items", [])


def _extract_doc_id(chunk: dict[str, Any]) -> str:
    metadata = chunk.get("metadata", {})
    return str(metadata.get("docId", ""))


def _extract_title(chunk: dict[str, Any]) -> str:
    metadata = chunk.get("metadata", {})
    return str(metadata.get("title", ""))
