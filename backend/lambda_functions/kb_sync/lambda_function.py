from __future__ import annotations

from typing import Any

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

from config.settings import settings
from handlers.kb_sync_handler import handle_eventbridge_event, handle_s3_event

logger = Logger(level=settings.log_level)
metrics = Metrics(namespace="KnowledgePortal", service="kb-sync")


@logger.inject_lambda_context(correlation_id_path="detail.requestId")
@metrics.log_metrics
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> Any:
    # S3 イベント (documents/ プレフィックスへの Put/Delete)
    if event.get("Records") and event["Records"][0].get("eventSource") == "aws:s3":
        return handle_s3_event(event)

    # EventBridge Scheduler (15 分間隔の追随同期)
    return handle_eventbridge_event(event)
