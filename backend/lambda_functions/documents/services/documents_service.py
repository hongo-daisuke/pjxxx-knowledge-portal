from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
)

from config.constants import (
    DEFAULT_PAGE_LIMIT,
    DOCUMENTS_PREFIX,
    MAX_PAGE_LIMIT,
    PRESIGNED_GET_EXPIRES,
    PRESIGNED_PUT_EXPIRES,
)
from config.settings import settings
from infrastructure.s3_handler import S3Handler
from repositories.documents_repository import DocumentsRepository
from shared.models import (
    CompleteUploadRequest,
    CreateDocumentRequest,
    Role,
    UpdateDocumentRequest,
    UserClaims,
)


class DocumentsService:
    def __init__(
        self,
        repository: DocumentsRepository | None = None,
        s3_handler: S3Handler | None = None,
    ) -> None:
        self._repo = repository or DocumentsRepository()
        self._s3 = s3_handler or S3Handler()

    def create_document(
        self,
        req: CreateDocumentRequest,
        claims: UserClaims,
    ) -> dict[str, Any]:
        doc_id = f"d_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc).isoformat()
        s3_key = f"{DOCUMENTS_PREFIX}/{doc_id}/v1/{req.file_name}"

        # DynamoDB に pending レコードを登録 (TTL: 1 時間)
        ttl = int(datetime.now(timezone.utc).timestamp()) + 3600
        self._repo.put_document({
            "doc_id": doc_id,
            "title": req.title,
            "description": req.description,
            "tags": req.tags,
            "department": req.department,
            "visibility": req.visibility.value,
            "owner_id": claims.sub,
            "latest_version": 0,
            "s3_key": s3_key,
            "file_type": req.content_type,
            "size": req.size,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "ttl": ttl,
            # GSI2 用
            "gsi2pk": f"DEPT#{req.department}" if req.department else "DEPT#",
            "gsi2sk": f"UPD#{now}",
        })

        presigned_url = self._s3.generate_presigned_put_url(
            key=s3_key,
            content_type=req.content_type,
            expires_in=PRESIGNED_PUT_EXPIRES,
        )

        return {"doc_id": doc_id, "presigned_url": presigned_url, "s3_key": s3_key}

    def complete_upload(
        self,
        doc_id: str,
        req: CompleteUploadRequest,
        claims: UserClaims,
    ) -> dict[str, Any]:
        doc = self._repo.get_document(doc_id)
        if not doc:
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        if doc.get("status") == "deleted":
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        if doc.get("owner_id") != claims.sub and claims.role != Role.ADMIN:
            raise UnauthorizedError("この文書を操作する権限がありません")

        s3_key = doc["s3_key"]
        head = self._s3.head_object(s3_key)
        size = head.get("ContentLength", 0)

        self._repo.update_document_status_active(
            doc_id=doc_id,
            s3_key=s3_key,
            size=size,
            latest_version=1,
        )

        # Bedrock KB 用メタデータサイドカーを生成
        self._s3.put_metadata_json(
            object_key=s3_key,
            doc_id=doc_id,
            title=doc["title"],
            visibility=doc["visibility"],
            department=doc.get("department", ""),
            owner_id=doc["owner_id"],
            tags=doc.get("tags", []),
        )

        # バージョンレコード登録
        self._repo.put_version({
            "doc_id": doc_id,
            "version": 1,
            "s3_key": s3_key,
            "uploaded_by": claims.sub,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "note": req.note,
            "size": size,
        })

        # タグ関連アイテム登録
        now = datetime.now(timezone.utc).isoformat()
        for tag in doc.get("tags", []):
            self._repo.put_tag_doc_relation(tag, doc_id, now)
            self._repo.increment_tag_count(tag)

        return {"doc_id": doc_id, "status": "active"}

    def list_documents(
        self,
        tag: str | None,
        department: str | None,
        keyword: str | None,
        next_token: str | None,
        limit: int,
    ) -> dict[str, Any]:
        limit = min(limit, MAX_PAGE_LIMIT)
        exclusive_start_key = _decode_next_token(next_token)

        if tag:
            result = self._repo.list_documents_by_tag(
                tag=tag, exclusive_start_key=exclusive_start_key, limit=limit
            )
        elif department:
            result = self._repo.list_documents_by_department(
                department=department, exclusive_start_key=exclusive_start_key, limit=limit
            )
        else:
            result = self._repo.scan_active_documents(
                exclusive_start_key=exclusive_start_key, limit=limit
            )

        items = result.get("Items", [])

        if keyword:
            kw = keyword.lower()
            items = [
                i for i in items
                if kw in i.get("title", "").lower() or kw in i.get("description", "").lower()
            ]

        next_key = result.get("LastEvaluatedKey")
        return {
            "items": [_format_doc(i) for i in items],
            "next_token": _encode_next_token(next_key),
        }

    def get_document(self, doc_id: str, claims: UserClaims) -> dict[str, Any]:
        doc = self._repo.get_document(doc_id)
        if not doc or doc.get("status") == "deleted":
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        _check_read_permission(doc, claims)
        versions = self._repo.list_versions(doc_id)
        return {**_format_doc(doc), "versions": versions}

    def update_document(
        self,
        doc_id: str,
        req: UpdateDocumentRequest,
        claims: UserClaims,
    ) -> dict[str, Any]:
        doc = self._repo.get_document(doc_id)
        if not doc or doc.get("status") == "deleted":
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        if doc.get("owner_id") != claims.sub and claims.role != Role.ADMIN:
            raise UnauthorizedError("この文書を更新する権限がありません")

        updates: dict[str, Any] = {}
        if req.title is not None:
            updates["title"] = req.title
        if req.description is not None:
            updates["description"] = req.description
        if req.tags is not None:
            updates["tags"] = req.tags
        if req.department is not None:
            updates["department"] = req.department
        if req.visibility is not None:
            updates["visibility"] = req.visibility.value

        if not updates:
            raise BadRequestError("更新する項目がありません")

        updated = self._repo.update_document_meta(doc_id, updates)

        # メタデータサイドカーを再生成
        if doc.get("s3_key") and doc.get("status") == "active":
            merged = {**doc, **updates}
            self._s3.put_metadata_json(
                object_key=doc["s3_key"],
                doc_id=doc_id,
                title=merged.get("title", ""),
                visibility=merged.get("visibility", "public"),
                department=merged.get("department", ""),
                owner_id=doc["owner_id"],
                tags=merged.get("tags", []),
            )

        return _format_doc(updated)

    def delete_document(self, doc_id: str, claims: UserClaims) -> None:
        doc = self._repo.get_document(doc_id)
        if not doc or doc.get("status") == "deleted":
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        if doc.get("owner_id") != claims.sub and claims.role != Role.ADMIN:
            raise UnauthorizedError("この文書を削除する権限がありません")

        self._repo.soft_delete_document(doc_id)

        # S3 からオブジェクトを削除 (次回 KB 同期でベクトルも削除される)
        if doc.get("s3_key"):
            self._s3.delete_object(doc["s3_key"])
            self._s3.delete_object(f"{doc['s3_key']}.metadata.json")

        # タグ関連アイテムとカウント更新
        for tag in doc.get("tags", []):
            self._repo.delete_tag_doc_relations(doc_id, [tag])
            self._repo.decrement_tag_count(tag)

    def get_download_url(self, doc_id: str, claims: UserClaims) -> dict[str, Any]:
        doc = self._repo.get_document(doc_id)
        if not doc or doc.get("status") != "active":
            raise NotFoundError(f"文書が見つかりません: {doc_id}")
        _check_read_permission(doc, claims)

        file_name = doc["s3_key"].split("/")[-1]
        url = self._s3.generate_presigned_get_url(
            key=doc["s3_key"],
            file_name=file_name,
            expires_in=PRESIGNED_GET_EXPIRES,
        )
        return {"presigned_url": url, "file_name": file_name}

    def list_tags(self) -> list[dict[str, Any]]:
        return self._repo.list_tags()


# --- ヘルパー ---

def _check_read_permission(doc: dict[str, Any], claims: UserClaims) -> None:
    visibility = doc.get("visibility", "public")
    if visibility == "public":
        return
    if visibility == "department" and doc.get("department") == claims.department:
        return
    if visibility == "private" and doc.get("owner_id") == claims.sub:
        return
    raise UnauthorizedError("この文書を閲覧する権限がありません")


def _format_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "doc_id": doc.get("doc_id", ""),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "tags": doc.get("tags", []),
        "department": doc.get("department", ""),
        "visibility": doc.get("visibility", "public"),
        "owner_id": doc.get("owner_id", ""),
        "latest_version": doc.get("latest_version", 0),
        "s3_key": doc.get("s3_key", ""),
        "file_type": doc.get("file_type", ""),
        "size": doc.get("size", 0),
        "status": doc.get("status", ""),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at", ""),
    }


def _decode_next_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    import base64
    import json
    try:
        return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception:
        raise BadRequestError("next_token が不正です")


def _encode_next_token(key: dict[str, Any] | None) -> str | None:
    if not key:
        return None
    import base64
    import json
    return base64.urlsafe_b64encode(json.dumps(key).encode()).decode()
