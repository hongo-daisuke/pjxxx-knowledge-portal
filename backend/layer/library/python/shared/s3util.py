from __future__ import annotations

import json
from typing import Any

import boto3


def generate_presigned_put_url(
    bucket: str,
    key: str,
    content_type: str,
    max_size_bytes: int = 100 * 1024 * 1024,
    expires_in: int = 900,
) -> str:
    """
    S3 presigned PUT URL を生成する。
    Content-Type と最大サイズを条件として埋め込む。
    """
    s3 = boto3.client("s3")
    url: str = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )
    return url


def generate_presigned_get_url(
    bucket: str,
    key: str,
    file_name: str,
    expires_in: int = 300,
) -> str:
    """
    S3 presigned GET URL を生成する (有効期限 5 分)。
    Content-Disposition で元ファイル名を付与する。
    """
    s3 = boto3.client("s3")
    url: str = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ResponseContentDisposition": f'attachment; filename="{file_name}"',
        },
        ExpiresIn=expires_in,
    )
    return url


def put_metadata_json(
    bucket: str,
    object_key: str,
    doc_id: str,
    title: str,
    visibility: str,
    department: str,
    owner_id: str,
    tags: list[str],
) -> None:
    """
    Bedrock Knowledge Base のサイドカーメタデータ JSON を S3 に配置する。
    配置先: <object_key>.metadata.json
    tags はカンマ結合文字列として格納する (KB のフィルタ可能メタデータ制約に合わせる)。
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
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=f"{object_key}.metadata.json",
        Body=json.dumps(metadata, ensure_ascii=False),
        ContentType="application/json",
    )


def head_object(bucket: str, key: str) -> dict[str, Any]:
    """S3 オブジェクトの存在・サイズを検証する。存在しない場合は ClientError を送出する。"""
    s3 = boto3.client("s3")
    return s3.head_object(Bucket=bucket, Key=key)  # type: ignore[no-any-return]


def delete_object(bucket: str, key: str) -> None:
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=bucket, Key=key)
