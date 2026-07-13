# exceptions.py
"""
Custom Business Logic Layer Exceptions.

This module defines the domain-specific business logic errors.
These exceptions are caught by FastAPI's global exception handlers (WEB/HTTP layer) to return standardized HTTP error responses.
"""


class AppError(Exception):
    """Exception Base Class for the application."""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


# --- Auth & Users ---
class InvalidCredentialsError(AppError):
    def __init__(self, detail: str = "Invalid credentials provided."):
        super().__init__(detail=detail, status_code=401)


class UserNotFoundError(AppError):
    def __init__(self, detail: str = "User not found."):
        super().__init__(detail=detail, status_code=404)


class UserAlreadyExistsError(AppError):
    def __init__(self, detail: str = "User already exists."):
        super().__init__(detail=detail, status_code=400)


class TokenError(AppError):
    def __init__(self, detail: str = "Not authenticated."):
        super().__init__(detail=detail, status_code=401)


# --- Workspace Core ---
class WorkspaceCreationError(AppError):
    def __init__(
        self,
        detail: str = "Could not create workspace due to an internal server error.",
    ):
        super().__init__(detail=detail, status_code=500)


class WorkspaceNotFoundError(AppError):
    def __init__(self, detail: str = "The requested workspace does not exist."):
        super().__init__(detail=detail, status_code=404)


class WorkspacePermissionError(AppError):
    def __init__(self, detail: str = "You do not have permission for this action."):
        super().__init__(detail=detail, status_code=403)


# --- Workspace Members ---
class UserAlreadyInWorkspaceError(AppError):
    def __init__(self, detail: str = "User is already part of the workspace."):
        super().__init__(detail=detail, status_code=400)


class AdminRemovalError(AppError):
    def __init__(self, detail: str = "Admins cannot be removed from the workspace."):
        super().__init__(detail=detail, status_code=403)


# --- Monitors ---
class MonitorNotFoundError(AppError):
    def __init__(self, detail: str = "The requested monitor does not exist."):
        super().__init__(detail=detail, status_code=404)


class UserNotInWorkspaceError(AppError):
    def __init__(self, detail: str = "User not in specified workspace"):
        super().__init__(detail=detail, status_code=400)


class MonitorPermissionError(AppError):
    def __init__(
        self, detail: str = "User does not have permission to modify this monitor"
    ):
        super().__init__(detail=detail, status_code=403)


# --- PingHistory ---
