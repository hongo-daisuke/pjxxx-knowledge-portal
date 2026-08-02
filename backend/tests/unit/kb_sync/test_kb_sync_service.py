"""KbSyncService の単体テスト。"""
from unittest.mock import MagicMock

import pytest

from services.kb_sync_service import KbSyncService


@pytest.fixture()
def mock_bedrock() -> MagicMock:
    mock = MagicMock()
    mock.has_running_job.return_value = False
    mock.start_ingestion_job.return_value = "job-001"
    return mock


@pytest.fixture()
def service(mock_bedrock: MagicMock) -> KbSyncService:
    return KbSyncService(bedrock=mock_bedrock)


class TestStartSync:
    def test_実行中ジョブなしの場合はjobを開始する(
        self, service: KbSyncService, mock_bedrock: MagicMock
    ) -> None:
        result = service.start_sync()

        assert result["skipped"] is False
        assert result["job_id"] == "job-001"
        mock_bedrock.start_ingestion_job.assert_called_once()

    def test_実行中ジョブありの場合はスキップ(
        self, service: KbSyncService, mock_bedrock: MagicMock
    ) -> None:
        mock_bedrock.has_running_job.return_value = True

        result = service.start_sync(force=False)

        assert result["skipped"] is True
        mock_bedrock.start_ingestion_job.assert_not_called()

    def test_force_Trueの場合は実行中でも開始する(
        self, service: KbSyncService, mock_bedrock: MagicMock
    ) -> None:
        mock_bedrock.has_running_job.return_value = True

        result = service.start_sync(force=True)

        assert result["skipped"] is False
        mock_bedrock.start_ingestion_job.assert_called_once()


class TestGetStatus:
    def test_jobsが空の場合(self, service: KbSyncService, mock_bedrock: MagicMock) -> None:
        mock_bedrock.list_ingestion_jobs.return_value = []

        result = service.get_status()

        assert result["jobs"] == []
        assert result["latest_status"] is None

    def test_最新ジョブの状態を返す(self, service: KbSyncService, mock_bedrock: MagicMock) -> None:
        mock_bedrock.list_ingestion_jobs.return_value = [
            {
                "ingestionJobId": "job-001",
                "status": "COMPLETE",
                "startedAt": "2026-07-12T00:00:00Z",
                "updatedAt": "2026-07-12T00:01:00Z",
                "statistics": {"numberOfDocumentsScanned": 5, "numberOfDocumentsIndexed": 5},
                "failureReasons": [],
            }
        ]

        result = service.get_status()

        assert result["latest_status"] == "COMPLETE"
        assert len(result["jobs"]) == 1
        assert result["jobs"][0]["statistics"]["numberOfDocumentsIndexed"] == 5
