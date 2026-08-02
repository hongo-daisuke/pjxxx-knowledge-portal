from __future__ import annotations

from typing import Any

import boto3

from config.settings import settings


class ChatRepository:
    """チャット履歴の DynamoDB 操作。"""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb")
        self._table = dynamodb.Table(settings.main_table_name)

    def save_history(self, item: dict[str, Any]) -> None:
        item["pk"] = f"USER#{item['user_id']}"
        item["sk"] = f"CHAT#{item['timestamp']}"
        self._table.put_item(Item=item)

    def list_history(
        self,
        user_id: str,
        limit: int = 20,
        exclusive_start_key: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from boto3.dynamodb.conditions import Key

        kwargs: dict[str, Any] = {
            "KeyConditionExpression": Key("pk").eq(f"USER#{user_id}") & Key("sk").begins_with("CHAT#"),
            "ScanIndexForward": False,
            "Limit": limit,
        }
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        return self._table.query(**kwargs)
