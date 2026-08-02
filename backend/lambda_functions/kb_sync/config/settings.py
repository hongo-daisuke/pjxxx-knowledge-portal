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
    def knowledge_base_id(self) -> str:
        return _require("KNOWLEDGE_BASE_ID")

    @property
    def data_source_id(self) -> str:
        return _require("DATA_SOURCE_ID")

    @property
    def log_level(self) -> str:
        return os.environ.get("LOG_LEVEL", "INFO")

    @property
    def environment(self) -> str:
        return _require("ENVIRONMENT")


settings = Settings()
