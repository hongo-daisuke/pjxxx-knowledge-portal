from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.exceptions import ClientError

from config.settings import settings


class S3Handler:
    """S3 への低レベル操作を担う。boto3 直接呼び出しはここのみ。"""

    def __init__(self) -> None:
        self._client = boto3.client("s3")
        self._bucket = settings.data_bucket_name

    def generate_presigned_put_url(
        self,
        key: str,
        content_type: str,
        expires_in: int = 900,
    ) -> str:
        url: str = self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return url

    def generate_presigned_get_url(
        self,
        key: str,
        file_name: str,
        expires_in: int = 300,
    ) -> str:
        url: str = self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ResponseContentDisposition": f'attachment; filename="{file_name}"',
            },
            ExpiresIn=expires_in,
        )
        return url

    def head_object(self, key: str) -> dict[str, Any]:
        return self._client.head_object(Bucket=self._bucket, Key=key)  # type: ignore[no-any-return]

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def put_metadata_json(
        self,
        object_key: str,
        doc_id: str,
        title: str,
        visibility: str,
        department: str,
        owner_id: str,
        tags: list[str],
    ) -> None:
        """
        Bedrock Knowledge Base 用のサイドカー metadata.json を配置する。
        tags はカンマ結合文字列として格納する (KB フィルタ可能メタデータ制約)。
        """
        metadata: dict[str, Any] = {
            "metadataAttributes": {
                "docId": doc_id,
                "title": title,
                "visibility": visibility,
                "department": department,
                "ownerId": owner_id,
                "tags": ",".join(tags),
            }
        }
        self._client.put_object(
            Bucket=self._bucket,
            Key=f"{object_key}.metadata.json",
            Body=json.dumps(metadata, ensure_ascii=False),
            ContentType="application/json",
        )
