from __future__ import annotations

from typing import Any

import boto3

from config.settings import settings


class BedrockAgentHandler:
    """Bedrock Agent (ingestion job) への低レベル呼び出し。"""

    def __init__(self) -> None:
        self._client = boto3.client("bedrock-agent")

    def start_ingestion_job(self) -> str:
        """ingestion job を開始し、job_id を返す。"""
        response = self._client.start_ingestion_job(
            knowledgeBaseId=settings.knowledge_base_id,
            dataSourceId=settings.data_source_id,
        )
        return response["ingestionJob"]["ingestionJobId"]

    def get_ingestion_job(self, job_id: str) -> dict[str, Any]:
        response = self._client.get_ingestion_job(
            knowledgeBaseId=settings.knowledge_base_id,
            dataSourceId=settings.data_source_id,
            ingestionJobId=job_id,
        )
        return response.get("ingestionJob", {})

    def list_ingestion_jobs(self, max_results: int = 5) -> list[dict[str, Any]]:
        response = self._client.list_ingestion_jobs(
            knowledgeBaseId=settings.knowledge_base_id,
            dataSourceId=settings.data_source_id,
            maxResults=max_results,
            sortBy={"attribute": "STARTED_AT", "order": "DESCENDING"},
        )
        return response.get("ingestionJobSummaries", [])

    def has_running_job(self) -> bool:
        """実行中の ingestion job が存在するかチェックする。"""
        jobs = self.list_ingestion_jobs(max_results=1)
        if not jobs:
            return False
        return jobs[0].get("status") in ("STARTING", "IN_PROGRESS")
