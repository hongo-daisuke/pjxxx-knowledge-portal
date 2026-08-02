from __future__ import annotations

from typing import Any

import boto3

from config.settings import settings

_SYSTEM_PROMPT = (
    "あなたは社内文書に基づいて質問に回答するアシスタントです。"
    "提供されたコンテキスト（社内文書の抜粋）のみを根拠として回答してください。"
    "コンテキストに記載のない情報は推測せず、「提供された文書には記載がありません」と回答してください。"
    "回答中で根拠にした箇所には [番号] の形式で出典番号を明示してください。"
)


class BedrockHandler:
    """Bedrock Knowledge Base の Retrieve と Converse API への低レベル呼び出し。"""

    def __init__(self) -> None:
        self._agent_rt = boto3.client("bedrock-agent-runtime")
        self._runtime = boto3.client("bedrock-runtime")

    def retrieve(
        self,
        question: str,
        filter_expression: dict,
    ) -> list[dict[str, Any]]:
        """KB から関連チャンクを取得する。"""
        response = self._agent_rt.retrieve(
            knowledgeBaseId=settings.knowledge_base_id,
            retrievalQuery={"text": question},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": settings.number_of_results,
                    "filter": filter_expression,
                }
            },
        )
        return response.get("retrievalResults", [])

    def converse(self, question: str, context_chunks: list[dict[str, Any]]) -> str:
        """取得チャンクを根拠コンテキストとして Converse API で回答生成する。"""
        context_text = "\n\n".join(
            f"[{i + 1}] {chunk.get('content', {}).get('text', '')}"
            for i, chunk in enumerate(context_chunks)
        )
        user_message = f"コンテキスト:\n{context_text}\n\n質問: {question}"

        response = self._runtime.converse(
            modelId=settings.model_id,
            system=[{"text": _SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            inferenceConfig={"maxTokens": 1024, "temperature": 0.0},
        )
        output = response.get("output", {}).get("message", {})
        content = output.get("content", [{}])
        return content[0].get("text", "") if content else ""
