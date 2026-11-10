"""Đổi lỗi nghiệp vụ thành mã HTTP và cấu trúc lỗi thống nhất của API contract:
{ "error": { "code": "...", "message": "...", "fields": {...} } }"""
import logging

import psycopg
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

    @app.exception_handler(psycopg.OperationalError)
    async def database_down(_: Request, e: psycopg.OperationalError):
        # Suy giảm có kiểm soát (C7): CSDL tắt thì báo rõ, không treo, không lộ lỗi thô của thư viện
        logging.getLogger("smartcrm").error("Không kết nối được CSDL: %s", e)
        return JSONResponse(status_code=503, content=body("DATABASE_UNAVAILABLE",
                            "Không kết nối được cơ sở dữ liệu. Vui lòng thử lại sau."))

    @app.exception_handler(Exception)
    async def unexpected(_: Request, e: Exception):
        logging.getLogger("smartcrm").exception("Lỗi không lường trước")
        return JSONResponse(status_code=500, content=body("INTERNAL_ERROR", "Máy chủ gặp lỗi, vui lòng thử lại."))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, e: RequestValidationError):
        if any(err.get("type") == "json_invalid" for err in e.errors()):      # thân yêu cầu không phải JSON hợp lệ
            return JSONResponse(status_code=400, content=body("VALIDATION_FAILED", "Dữ liệu không hợp lệ",
                                                              {"body": "JSON không hợp lệ"}))
        fields = {".".join(str(x) for x in err["loc"] if x not in ("body", "query", "path")): vi(err) for err in e.errors()}
        return JSONResponse(status_code=400, content=body("VALIDATION_FAILED", "Dữ liệu không hợp lệ", fields))
