# main.py
"""
Main Application Entrypoint.
"""

import uvicorn
from exceptions import (
    AdminCantBeRemoved,
    InvalidCredentialsError,
    TokenError,
    UserAlreadyExist,
    UserAlreadyInWorkspace,
    UserNotFound,
    WorkspaceCreationError,
    WorkspaceNoAuthorization,
    WorkspaceNotFound,
)
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from logger_setup import LOGGING_CONFIG, setup_logging
from routers.auth import router_auth
from routers.protected import router_protected
from routers.workspace import workspace_router
from sqlalchemy.exc import SQLAlchemyError

logger = setup_logging()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: centralize routers into refactored backend/api and import only the api router which includes all other routers
# TODO: follow the same router naming convention for all routes

app.include_router(router_auth)
app.include_router(router_protected)
app.include_router(workspace_router)


@app.exception_handler(TokenError)
async def token_error_handler(request: Request, exc: TokenError):
    logger.warning(f"Authentication blocked: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Not authenticated"},
    )


@app.exception_handler(UserAlreadyExist)
async def user_exists_handler(request: Request, exc: UserAlreadyExist):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database crash intercepted: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "An internal database error occured."}
    )


@app.exception_handler(WorkspaceNotFound)
async def workspace_not_found_error(request: Request, exc: WorkspaceNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(WorkspaceCreationError)
async def workpace_creation_error_handler(
    request: Request, exc: WorkspaceCreationError
):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(UserNotFound)
async def user_not_found_error_handler(request: Request, exc: UserNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(WorkspaceNoAuthorization)
async def workspace_no_role_handler(request: Request, exc: WorkspaceNoAuthorization):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyInWorkspace)
async def user_already_in_workspace_handler(
    request: Request, exc: UserAlreadyInWorkspace
):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(AdminCantBeRemoved)
async def admin_cant_be_removed_handler(request: Request, exc: AdminCantBeRemoved):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    logger.info("User logged out.")
    return {"message": "Logged out"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG,  # might break here
        reload=False,  # set to True
    )
