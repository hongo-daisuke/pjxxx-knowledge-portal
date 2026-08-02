from __future__ import annotations

from typing import Any

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit

from infrastructure.bedrock_handler import BedrockAgentHandler

logger = Logger()
metrics = Metrics(namespace="KnowledgePortal", service="kb-sync")


class KbSyncService:
    def __init__(self, bedrock: BedrockAgentHandler | None = None) -> None:
        self._bedrock = bedrock or BedrockAgentHandler()

    def start_sync(self, force: bool = False) -> dict[str, Any]:
        """
        ingestion job を開始する。
        実行中のジョブが既にある場合はスキップする (KB は直列実行のみサポート)。
        force=True の場合はスキップしない (手動同期用)。
        """
        if not force and self._bedrock.has_running_job():
            logger.info("ingestion job は既に実行中のためスキップします")
            return {"skipped": True, "reason": "job already running"}

        job_id = self._bedrock.start_ingestion_job()
        logger.info("ingestion job を開始しました", extra={"job_id": job_id})
        metrics.add_metric(name="IngestionJobStarted", unit=MetricUnit.Count, value=1)

        return {"job_id": job_id, "skipped": False}

    def get_status(self) -> dict[str, Any]:
        """直近の ingestion job の状態と統計を返す。"""
        jobs = self._bedrock.list_ingestion_jobs(max_results=5)
        if not jobs:
            return {"jobs": [], "latest_status": None}

        latest = jobs[0]
        return {
            "jobs": [_format_job(j) for j in jobs],
            "latest_status": latest.get("status"),
        }


def _format_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job.get("ingestionJobId", ""),
        "status": job.get("status", ""),
        "started_at": job.get("startedAt", ""),
        "updated_at": job.get("updatedAt", ""),
        "statistics": job.get("statistics", {}),
        "failure_reasons": job.get("failureReasons", []),
    }
