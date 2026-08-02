from __future__ import annotations

from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr, Key

from config.settings import settings


class DynamoHandler:
    """DynamoDB への低レベル操作を担う。boto3 直接呼び出しはここのみ。"""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb")
        self._table = dynamodb.Table(settings.main_table_name)

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

    def query_by_pk(
        self,
        pk: str,
        sk_begins_with: str | None = None,
        scan_index_forward: bool = True,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        condition = Key("pk").eq(pk)
        if sk_begins_with:
            condition = condition & Key("sk").begins_with(sk_begins_with)
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": condition,
            "ScanIndexForward": scan_index_forward,
        }
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
        filter_expression: Any = None,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "IndexName": index_name,
            "KeyConditionExpression": Key(pk_name).eq(pk_value),
            "ScanIndexForward": scan_index_forward,
        }
        if filter_expression is not None:
            kwargs["FilterExpression"] = filter_expression
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        if limit:
            kwargs["Limit"] = limit
        return self._table.query(**kwargs)

    def scan_with_filter(
        self,
        filter_expression: Any,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"FilterExpression": filter_expression}
        if exclusive_start_key:
            kwargs["ExclusiveStartKey"] = exclusive_start_key
        if limit:
            kwargs["Limit"] = limit
        return self._table.scan(**kwargs)
