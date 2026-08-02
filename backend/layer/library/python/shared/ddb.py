from __future__ import annotations

from typing import Any

import boto3
from boto3.dynamodb.conditions import Key


class BaseRepository:
    """DynamoDB シングルテーブルの基底クラス。boto3 低レベル呼び出しは行わない。"""

    def __init__(self, table_name: str) -> None:
        dynamodb = boto3.resource("dynamodb")
        self._table = dynamodb.Table(table_name)

    def get_item(self, pk: str, sk: str) -> dict[str, Any] | None:
        response = self._table.get_item(Key={"pk": pk, "sk": sk})
        return response.get("Item")

    def put_item(self, item: dict[str, Any]) -> None:
        self._table.put_item(Item=item)

    def update_item(
        self,
        pk: str,
        sk: str,
        update_expression: str,
        expression_values: dict[str, Any],
        expression_names: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "Key": {"pk": pk, "sk": sk},
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_values,
            "ReturnValues": "ALL_NEW",
        }
        if expression_names:
            kwargs["ExpressionAttributeNames"] = expression_names
        response = self._table.update_item(**kwargs)
        return response.get("Attributes", {})

    def delete_item(self, pk: str, sk: str) -> None:
        self._table.delete_item(Key={"pk": pk, "sk": sk})

    def query(
        self,
        key_condition: Any,
        index_name: str | None = None,
        filter_expression: Any = None,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int | None = None,
        scan_index_forward: bool = True,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": key_condition,
            "ScanIndexForward": scan_index_forward,
        }
        if index_name:
            kwargs["IndexName"] = index_name
        if filter_expression is not None:
            kwargs["FilterExpression"] = filter_expression
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        if limit:
            kwargs["Limit"] = limit
        return self._table.query(**kwargs)

    def query_gsi(
        self,
        index_name: str,
        pk_name: str,
        pk_value: str,
        scan_index_forward: bool = False,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self.query(
            key_condition=Key(pk_name).eq(pk_value),
            index_name=index_name,
            scan_index_forward=scan_index_forward,
            exclusive_start_key=exclusive_start_key,
            limit=limit,
        )
