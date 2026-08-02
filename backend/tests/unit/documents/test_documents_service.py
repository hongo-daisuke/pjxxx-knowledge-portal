"""DocumentsService の単体テスト。Repository と S3Handler をモックで差し替える。"""
from unittest.mock import MagicMock, patch

import pytest

from services.documents_service import DocumentsService
from shared.models import (
    CompleteUploadRequest,
    CreateDocumentRequest,
    Role,
    UserClaims,
    Visibility,
)


def _make_claims(role: Role = Role.EDITOR) -> UserClaims:
    return UserClaims(sub="user-001", email="test@example.com", department="keiri", role=role)


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def mock_s3() -> MagicMock:
    mock = MagicMock()
    mock.generate_presigned_put_url.return_value = "https://s3.example.com/presigned"
    return mock


@pytest.fixture()
def service(mock_repo: MagicMock, mock_s3: MagicMock) -> DocumentsService:
    return DocumentsService(repository=mock_repo, s3_handler=mock_s3)


class TestCreateDocument:
    def test_正常系_presignedUrlとdocIdを返す(
        self, service: DocumentsService, mock_repo: MagicMock, mock_s3: MagicMock
    ) -> None:
        req = CreateDocumentRequest(
            title="テスト文書",
            file_name="test.pdf",
            content_type="application/pdf",
            size=1024,
        )
        result = service.create_document(req, _make_claims())

        assert "doc_id" in result
        assert result["presigned_url"] == "https://s3.example.com/presigned"
        mock_repo.put_document.assert_called_once()

    def test_pendingレコードにTTLが設定される(
        self, service: DocumentsService, mock_repo: MagicMock
    ) -> None:
        req = CreateDocumentRequest(
            title="テスト文書",
            file_name="test.pdf",
            content_type="application/pdf",
            size=1024,
        )
        service.create_document(req, _make_claims())

        call_args = mock_repo.put_document.call_args[0][0]
        assert "ttl" in call_args
        assert call_args["status"] == "pending"


class TestCompleteUpload:
    def test_正常系_statusがactiveになる(
        self, service: DocumentsService, mock_repo: MagicMock, mock_s3: MagicMock
    ) -> None:
        mock_repo.get_document.return_value = {
            "doc_id": "d_001",
            "title": "テスト",
            "owner_id": "user-001",
            "status": "pending",
            "s3_key": "documents/d_001/v1/test.pdf",
            "visibility": "public",
            "department": "keiri",
            "tags": ["経理"],
        }
        mock_s3.head_object.return_value = {"ContentLength": 2048}

        result = service.complete_upload("d_001", CompleteUploadRequest(), _make_claims())

        assert result["status"] == "active"
        mock_repo.update_document_status_active.assert_called_once()
        mock_s3.put_metadata_json.assert_called_once()

    def test_存在しない文書はNotFoundError(
        self, service: DocumentsService, mock_repo: MagicMock
    ) -> None:
        from aws_lambda_powertools.event_handler.exceptions import NotFoundError

        mock_repo.get_document.return_value = None

        with pytest.raises(NotFoundError):
            service.complete_upload("nonexistent", CompleteUploadRequest(), _make_claims())

    def test_他人の文書はUnauthorizedError(
        self, service: DocumentsService, mock_repo: MagicMock
    ) -> None:
        from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

        mock_repo.get_document.return_value = {
            "doc_id": "d_002",
            "owner_id": "other-user",
            "status": "pending",
            "s3_key": "documents/d_002/v1/file.pdf",
        }
        other_claims = UserClaims(sub="user-001", role=Role.EDITOR)

        with pytest.raises(UnauthorizedError):
            service.complete_upload("d_002", CompleteUploadRequest(), other_claims)


class TestDeleteDocument:
    def test_正常系_論理削除とS3削除が実行される(
        self, service: DocumentsService, mock_repo: MagicMock, mock_s3: MagicMock
    ) -> None:
        mock_repo.get_document.return_value = {
            "doc_id": "d_003",
            "owner_id": "user-001",
            "status": "active",
            "s3_key": "documents/d_003/v1/file.pdf",
            "tags": ["テスト"],
        }

        service.delete_document("d_003", _make_claims())

        mock_repo.soft_delete_document.assert_called_once_with("d_003")
        assert mock_s3.delete_object.call_count == 2  # ファイル本体 + metadata.json
