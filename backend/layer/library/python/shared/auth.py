from __future__ import annotations

from shared.models import Role, UserClaims


def extract_claims(event: dict) -> UserClaims:
    """API Gateway の requestContext から Cognito claims を抽出する。"""
    context = event.get("requestContext", {})
    authorizer = context.get("authorizer", {})
    claims = authorizer.get("claims", {})

    groups_raw: str = claims.get("cognito:groups", "")
    groups = [g.strip() for g in groups_raw.split(",") if g.strip()] if groups_raw else []

    role = _resolve_role(groups)

    return UserClaims(
        sub=claims.get("sub", ""),
        email=claims.get("email", ""),
        department=claims.get("custom:department", ""),
        role=role,
        groups=groups,
    )


def _resolve_role(groups: list[str]) -> Role:
    if "admin" in groups:
        return Role.ADMIN
    if "editor" in groups:
        return Role.EDITOR
    return Role.VIEWER


def require_editor(claims: UserClaims) -> None:
    """editor 以上でなければ 403 を送出する。"""
    from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

    if claims.role not in (Role.EDITOR, Role.ADMIN):
        raise UnauthorizedError("editor 権限が必要です")


def require_admin(claims: UserClaims) -> None:
    """admin でなければ 403 を送出する。"""
    from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError

    if claims.role != Role.ADMIN:
        raise UnauthorizedError("admin 権限が必要です")
