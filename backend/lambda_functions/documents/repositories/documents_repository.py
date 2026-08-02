from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from boto3.dynamodb.conditions import Attr

from config.constants import GSI1, GSI2, PK_DOC, PK_TAG, SK_META, SK_VER_PREFIX
from infrastructure.dynamo_handler import DynamoHandler


class DocumentsRepository:
    """DynamoDB シングルテーブルの文書・バージョン・タグ操作。"""

    def __init__(self, handler: DynamoHandler | None = None) -> None:
        self._ddb = handler or DynamoHandler()

    # --- 文書メタ ---

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        return self._ddb.get_item(pk=f"{PK_DOC}{doc_id}", sk=SK_META)

    def put_document(self, item: dict[str, Any]) -> None:
        item["pk"] = f"{PK_DOC}{item['doc_id']}"
        item["sk"] = SK_META
        self._ddb.put_item(item)

    def update_document_status_active(
        self,
        doc_id: str,
        s3_key: str,
        size: int,
        latest_version: int,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._ddb.update_item(
            pk=f"{PK_DOC}{doc_id}",
            sk=SK_META,
            update_expression=(
                "SET #st = :st, s3_key = :s3_key, #sz = :sz, "
                "latest_version = :lv, updated_at = :ua REMOVE #ttl"
            ),
            expression_values={
                ":st": "active",
                ":s3_key": s3_key,
                ":sz": size,
                ":lv": latest_version,
                ":ua": now,
            },
            expression_names={"#st": "status", "#sz": "size", "#ttl": "ttl"},
        )

    def update_document_meta(
        self,
        doc_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        set_parts = ["updated_at = :ua"]
        expr_values: dict[str, Any] = {":ua": now}

        for field, value in updates.items():
            set_parts.append(f"{field} = :{field}")
            expr_values[f":{field}"] = value

        return self._ddb.update_item(
            pk=f"{PK_DOC}{doc_id}",
            sk=SK_META,
            update_expression="SET " + ", ".join(set_parts),
            expression_values=expr_values,
        )

    def soft_delete_document(self, doc_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._ddb.update_item(
            pk=f"{PK_DOC}{doc_id}",
            sk=SK_META,
            update_expression="SET #st = :st, updated_at = :ua",
            expression_values={":st": "deleted", ":ua": now},
            expression_names={"#st": "status"},
        )

    def list_documents_by_tag(
        self,
        tag: str,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return self._ddb.query_gsi(
            index_name=GSI1,
            pk_name="gsi1pk",
            pk_value=f"{PK_TAG}{tag}",
            scan_index_forward=False,
            filter_expression=Attr("status").eq("active"),
            exclusive_start_key=exclusive_start_key,
            limit=limit,
        )

    def list_documents_by_department(
        self,
        department: str,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return self._ddb.query_gsi(
            index_name=GSI2,
            pk_name="gsi2pk",
            pk_value=f"DEPT#{department}",
            scan_index_forward=False,
            filter_expression=Attr("status").eq("active"),
            exclusive_start_key=exclusive_start_key,
            limit=limit,
        )

    def scan_active_documents(
        self,
        exclusive_start_key: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        return self._ddb.scan_with_filter(
            filter_expression=Attr("status").eq("active") & Attr("sk").eq(SK_META),
            exclusive_start_key=exclusive_start_key,
            limit=limit,
        )

    def put_tag_doc_relation(self, tag: str, doc_id: str, updated_at: str) -> None:
        """GSI1 用のタグ→文書関連アイテムを登録する。"""
        self._ddb.put_item({
            "pk": f"{PK_TAG}{tag}",
            "sk": f"{PK_DOC}{doc_id}",
            "gsi1pk": f"{PK_TAG}{tag}",
            "gsi1sk": f"UPD#{updated_at}",
            "doc_id": doc_id,
        })

    def delete_tag_doc_relations(self, doc_id: str, tags: list[str]) -> None:
        for tag in tags:
            self._ddb.delete_item(pk=f"{PK_TAG}{tag}", sk=f"{PK_DOC}{doc_id}")

    # --- タグカウント ---

    def increment_tag_count(self, tag: str) -> None:
        self._ddb.update_item(
            pk=f"{PK_TAG}{tag}",
            sk=SK_META,
            update_expression="SET tag_name = :tn ADD #cnt :one",
            expression_values={":tn": tag, ":one": 1},
            expression_names={"#cnt": "count"},
        )

    def decrement_tag_count(self, tag: str) -> None:
        self._ddb.update_item(
            pk=f"{PK_TAG}{tag}",
            sk=SK_META,
            update_expression="ADD #cnt :minus",
            expression_values={":minus": -1},
            expression_names={"#cnt": "count"},
        )

    def list_tags(self) -> list[dict[str, Any]]:
        result = self._ddb.query_gsi(
            index_name=GSI1,
            pk_name="gsi1pk",
            pk_value="TAGS",
            scan_index_forward=True,
        )
        return result.get("Items", [])

    # --- バージョン ---

    def put_version(self, item: dict[str, Any]) -> None:
        version_str = str(item["version"]).zfill(6)
        item["pk"] = f"{PK_DOC}{item['doc_id']}"
        item["sk"] = f"{SK_VER_PREFIX}{version_str}"
        self._ddb.put_item(item)

    def list_versions(self, doc_id: str) -> list[dict[str, Any]]:
        result = self._ddb.query_by_pk(
            pk=f"{PK_DOC}{doc_id}",
            sk_begins_with=SK_VER_PREFIX,
            scan_index_forward=False,
        )
        return result.get("Items", [])
