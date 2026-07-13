# main.py
"""
Main Application Entrypoint.
"""

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.v1.router import api_router
from backend.app.core.exceptions import (
    AppError,
    TokenError,
)
from backend.app.core.logger_setup import LOGGING_CONFIG, setup_logging

logger = setup_logging()

app = FastAPI(
    title="PulseCheck API",
    description="API for PulseCheck, a monitoring and alerting platform.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(api_router, prefix="/api/v1", tags=["API v1"])
app.include_router(api_router)
# TODO: centralize routers into refactored backend/api and import only the api router which includes all other routers
# TODO: follow the same router naming convention for all routes


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    if exc.status_code >= 500:
        logger.error(f"Internal Server Error: {exc.detail}")
    else:
        logger.warning(f"Business logic error [{exc.status_code}]: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(TokenError)
async def token_error_handler(request: Request, exc: TokenError):
    logger.warning(f"Authentication blocked: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Not authenticated"},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database crash intercepted: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "An internal database error occured."}
    )


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    logger.info("User logged out.")
    return {"message": "Logged out"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",  # refactor path
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG,  # might break here
        reload=False,  # set to True
    )
