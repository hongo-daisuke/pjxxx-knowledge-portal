from __future__ import annotations

import os


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"環境変数 {name} が設定されていません")
    return value


class Settings:
    @property
    def main_table_name(self) -> str:
        return _require("MAIN_TABLE_NAME")

    @property
    def idempotency_table_name(self) -> str:
        return _require("IDEMPOTENCY_TABLE_NAME")

    @property
    def data_bucket_name(self) -> str:
        return _require("DATA_BUCKET_NAME")

    @property
    def log_level(self) -> str:
        return os.environ.get("LOG_LEVEL", "INFO")

    @property
    def environment(self) -> str:
        return _require("ENVIRONMENT")


settings = Settings()
