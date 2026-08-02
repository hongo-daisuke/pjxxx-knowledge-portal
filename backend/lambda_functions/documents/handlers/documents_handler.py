from __future__ import annotations

from aws_lambda_powertools.event_handler.api_gateway import Router

from services.documents_service import DocumentsService
from shared.auth import extract_claims, require_editor
from shared.models import (
    CompleteUploadRequest,
    CreateDocumentRequest,
    UpdateDocumentRequest,
)

router = Router()
_service = DocumentsService()


@router.post("/documents")
def create_document() -> dict:
    claims = extract_claims(router.current_event.raw_event)
    require_editor(claims)
    req = CreateDocumentRequest.model_validate(router.current_event.json_body)
    return _service.create_document(req, claims)


@router.post("/documents/<doc_id>/complete")
def complete_upload(doc_id: str) -> dict:
    claims = extract_claims(router.current_event.raw_event)
    require_editor(claims)
    req = CompleteUploadRequest.model_validate(router.current_event.json_body or {})
    return _service.complete_upload(doc_id, req, claims)


@router.get("/documents")
def list_documents() -> dict:
    claims = extract_claims(router.current_event.raw_event)
    params = router.current_event.query_string_parameters or {}
    limit = int(params.get("limit", 20))
    return _service.list_documents(
        tag=params.get("tag"),
        department=params.get("department"),
        keyword=params.get("q"),
        next_token=params.get("next_token"),
        limit=limit,
    )


@router.get("/documents/<doc_id>")
def get_document(doc_id: str) -> dict:
    claims = extract_claims(router.current_event.raw_event)
    return _service.get_document(doc_id, claims)


@router.put("/documents/<doc_id>")
def update_document(doc_id: str) -> dict:
    claims = extract_claims(router.current_event.raw_event)
    require_editor(claims)
    req = UpdateDocumentRequest.model_validate(router.current_event.json_body)
    return _service.update_document(doc_id, req, claims)


@router.delete("/documents/<doc_id>")
def delete_document(doc_id: str) -> dict:
    claims = extract_claims(router.current_event.raw_event)
    require_editor(claims)
    _service.delete_document(doc_id, claims)
    return {}


@router.post("/documents/<doc_id>/download-url")
def get_download_url(doc_id: str) -> dict:
    claims = extract_claims(router.current_event.raw_event)
    return _service.get_download_url(doc_id, claims)


@router.get("/tags")
def list_tags() -> dict:
    return {"tags": _service.list_tags()}
