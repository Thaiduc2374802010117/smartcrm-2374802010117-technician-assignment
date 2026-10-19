"""Lỗi nghiệp vụ. Lớp trình bày (api/errors.py) đổi các lỗi này thành mã HTTP theo API contract."""


class DomainError(Exception):
    code = "DOMAIN_ERROR"

    def __init__(self, message: str, code: str | None = None, fields: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.fields = fields or {}


class ValidationFailed(DomainError):   # -> 400
    code = "VALIDATION_FAILED"


class Forbidden(DomainError):          # -> 403
    code = "FORBIDDEN"


class NotFound(DomainError):           # -> 404
    code = "NOT_FOUND"


class InvalidState(DomainError):       # -> 409
    code = "INVALID_STATE"


class RuleViolation(DomainError):      # -> 422
    code = "RULE_VIOLATION"
