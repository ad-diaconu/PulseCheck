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


class UserNotFound(AppError):
    pass


class UserAlreadyExist(AppError):
    pass


class TokenError(AppError):
    pass


class WorkspaceCreationError(AppError):
    pass


class WorkspaceNotFound(AppError):
    pass


class WorkspaceNoAuthorization(AppError):
    pass


class UserAlreadyInWorkspace(AppError):
    pass


class AdminCantBeRemoved(AppError):
    pass
