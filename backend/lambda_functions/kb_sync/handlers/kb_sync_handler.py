from __future__ import annotations

from typing import Any

from aws_lambda_powertools import Logger

from services.kb_sync_service import KbSyncService

logger = Logger()
# Phase 1: S3 イベント + EventBridge スケジュールからのみ起動する。
# API #12 (POST /kb/sync) / #13 (GET /kb/status) は Phase 2 で追加予定。
_service = KbSyncService()


def handle_s3_event(event: dict[str, Any]) -> dict[str, Any]:
    """S3 イベント (documents/ プレフィックスへの Put/Delete) から自動同期を起動する。"""
    records = event.get("Records", [])
    if not records:
        return {"message": "no records"}
    logger.info("S3 イベントを受信しました", extra={"record_count": len(records)})
    return _service.start_sync(force=False)


def handle_eventbridge_event(event: dict[str, Any]) -> dict[str, Any]:
    """EventBridge Scheduler (15 分間隔) からの追随同期。"""
    logger.info("EventBridge スケジュールによる追随同期を開始します")
    return _service.start_sync(force=False)
