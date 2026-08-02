from __future__ import annotations

from shared.models import UserClaims

_PUBLIC_ONLY_FILTER: dict = {"equals": {"key": "visibility", "value": "public"}}


def build_full_filter(department: str, user_sub: str) -> dict:
    """
    権限フィルタ完全版: public ∪ 自部署 ∪ 自分の private の orAll 構造。

    Phase 2 (F-303) で build_retrieval_filter からの配線を切り替える。
    注意: ownerId / visibility / department は KB メタデータキー (camelCase 固定)。
          axios の camelCase↔snake_case 変換とは無関係なため変換不要。
    """
    conditions: list[dict] = [
        {"equals": {"key": "visibility", "value": "public"}},
    ]
    if department:
        conditions.append({
            "andAll": [
                {"equals": {"key": "visibility", "value": "department"}},
                {"equals": {"key": "department", "value": department}},
            ]
        })
    if user_sub:
        conditions.append({
            "andAll": [
                {"equals": {"key": "visibility", "value": "private"}},
                {"equals": {"key": "ownerId", "value": user_sub}},
            ]
        })
    return {"orAll": conditions} if len(conditions) > 1 else conditions[0]


def build_retrieval_filter(claims: UserClaims) -> dict:
    """
    chat_service から呼ばれる公開関数。

    Phase 1: visibility=public 固定 (安全側)。
             P1 期間中に department/private 文書が登録されても RAG 回答に漏れない。
    Phase 2: 下記 1 行に切り替える。
             return build_full_filter(claims.department or "", claims.sub or "")
    """
    return _PUBLIC_ONLY_FILTER
