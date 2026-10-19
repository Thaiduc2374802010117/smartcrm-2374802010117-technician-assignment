"""Đổi lỗi nghiệp vụ thành mã HTTP và cấu trúc lỗi thống nhất của API contract:
{ "error": { "code": "...", "message": "...", "fields": {...} } }"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ..services.errors import DomainError, Forbidden, InvalidState, NotFound, RuleViolation, ValidationFailed

STATUS = {ValidationFailed: 400, Forbidden: 403, NotFound: 404, InvalidState: 409, RuleViolation: 422}


class Unauthenticated(DomainError):
    code = "UNAUTHENTICATED"


def body(code, message, fields=None):
    return {"error": {"code": code, "message": message, "fields": fields or {}}}


def vi(err) -> str:
    """Thông báo lỗi kiểm tra kiểu dữ liệu bằng tiếng Việt."""
    t = err.get("type", "")
    if t == "missing":
        return "Trường bắt buộc"
    if t in ("int_parsing", "int_type"):
        return "Phải là số nguyên"
    if t == "greater_than":
        return "Phải là số nguyên dương"
    return "Giá trị không hợp lệ"


def register(app):
    @app.exception_handler(DomainError)
    async def domain_error(_: Request, e: DomainError):
        status = 401 if isinstance(e, Unauthenticated) else next((s for t, s in STATUS.items() if isinstance(e, t)), 400)
        return JSONResponse(status_code=status, content=body(e.code, e.message, e.fields))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, e: RequestValidationError):
        fields = {".".join(str(x) for x in err["loc"] if x not in ("body", "query", "path")): vi(err) for err in e.errors()}
        return JSONResponse(status_code=400, content=body("VALIDATION_FAILED", "Dữ liệu không hợp lệ", fields))
