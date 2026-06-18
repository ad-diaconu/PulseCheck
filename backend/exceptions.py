# exceptions.py
"""
Custom Business Logic Layer Exceptions.

This module defines the domain-specific business logic errors.
These exceptions are caught by FastAPI's global exception handlers (WEB/HTTP layer) to return standardized HTTP error responses.
"""


class AppError(Exception):
    """Exception Base Class for the application."""

    pass


class InvalidCredentialsError(AppError):
    pass


class UserAlreadyExist(AppError):
    pass


class TokenError(AppError):
    pass
