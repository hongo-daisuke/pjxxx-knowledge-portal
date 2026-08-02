"""kb_filter の単体テスト。

- build_retrieval_filter: P1 の公開関数 (public 固定)
- build_full_filter: P2 移行先の完全版 (orAll) — 常時テストを維持し P2 で即利用できる状態を保つ
"""
from shared.kb_filter import build_full_filter, build_retrieval_filter
from shared.models import Role, UserClaims


def _make_claims(
    sub: str = "user-001",
    department: str = "keiri",
    role: Role = Role.VIEWER,
) -> UserClaims:
    return UserClaims(sub=sub, department=department, role=role)


class TestBuildRetrievalFilterP1:
    """公開関数: P1 では常に public 固定フィルタを返す。"""

    def test_常に_visibility_public_の単一フィルタを返す(self) -> None:
        result = build_retrieval_filter(_make_claims())
        assert result == {"equals": {"key": "visibility", "value": "public"}}

    def test_部署なしユーザーでも同じフィルタを返す(self) -> None:
        result = build_retrieval_filter(_make_claims(department=""))
        assert result == {"equals": {"key": "visibility", "value": "public"}}

    def test_admin_ユーザーでも同じフィルタを返す(self) -> None:
        result = build_retrieval_filter(_make_claims(role=Role.ADMIN))
        assert result == {"equals": {"key": "visibility", "value": "public"}}


class TestBuildFullFilter:
    """完全版フィルタ: build_full_filter を直接テストする (P2 移行後に公開関数から呼ばれる)。"""

    def test_部署あり_sub_ありのユーザーは3条件のorAllになる(self) -> None:
        result = build_full_filter(department="keiri", user_sub="user-001")

        assert "orAll" in result
        assert len(result["orAll"]) == 3

    def test_public条件が必ず含まれる(self) -> None:
        result = build_full_filter(department="keiri", user_sub="user-001")
        public_cond = {"equals": {"key": "visibility", "value": "public"}}
        assert public_cond in result["orAll"]

    def test_部署なしユーザーは2条件のorAllになる(self) -> None:
        result = build_full_filter(department="", user_sub="user-002")

        assert "orAll" in result
        assert len(result["orAll"]) == 2

    def test_private条件に正しいownerIdが設定される(self) -> None:
        result = build_full_filter(department="sales", user_sub="user-999")

        private_cond = next(
            (c for c in result["orAll"] if "andAll" in c and
             any(a.get("equals", {}).get("value") == "private" for a in c["andAll"])),
            None,
        )
        assert private_cond is not None
        owner_filter = next(
            a for a in private_cond["andAll"]
            if a.get("equals", {}).get("key") == "ownerId"
        )
        assert owner_filter["equals"]["value"] == "user-999"

    def test_department条件に正しい部署が設定される(self) -> None:
        result = build_full_filter(department="hr", user_sub="user-003")

        dept_cond = next(
            (c for c in result["orAll"] if "andAll" in c and
             any(a.get("equals", {}).get("value") == "department" for a in c["andAll"])),
            None,
        )
        assert dept_cond is not None
        dept_filter = next(
            a for a in dept_cond["andAll"]
            if a.get("equals", {}).get("key") == "department"
        )
        assert dept_filter["equals"]["value"] == "hr"

    def test_ownerIdキー名がs3utilのmetadataAttributesと一致する(self) -> None:
        """
        KB メタデータキー (ownerId) が s3util.put_metadata_json の
        metadataAttributes と一致していることを確認する。
        axios の camelCase 変換は Lambda 内部の KB 呼び出しには適用されないため、
        両者は camelCase で統一されている必要がある。
        """
        result = build_full_filter(department="", user_sub="any-sub")
        private_cond = next(
            (c for c in result["orAll"] if "andAll" in c and
             any(a.get("equals", {}).get("value") == "private" for a in c["andAll"])),
            None,
        )
        assert private_cond is not None
        owner_key = next(
            a["equals"]["key"] for a in private_cond["andAll"]
            if a.get("equals", {}).get("key") == "ownerId"
        )
        assert owner_key == "ownerId", "KB フィルタキーは s3util の metadataAttributes['ownerId'] と一致する必要がある"

    def test_部署も_sub_もない場合はpublic単一フィルタを返す(self) -> None:
        result = build_full_filter(department="", user_sub="")
        assert result == {"equals": {"key": "visibility", "value": "public"}}
