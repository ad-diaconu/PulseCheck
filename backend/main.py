# main.py
"""
Main Application Entrypoint.
"""

import uvicorn
from exceptions import InvalidCredentialsError, TokenError, UserAlreadyExist
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from logger_setup import LOGGING_CONFIG, setup_logging
from routers.auth import router_auth
from routers.protected import router_protected
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

app.include_router(router_auth)
app.include_router(router_protected)


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


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    logger.info("User logged out.")
    return {"message": "Logged out"}


# @app.get("/protected-users")
# def get_users(payload: dict = Depends(verify_jwt)):
#     logger.info(f"User {payload.get('sub')} accessed users list.")
#     return {"users": fake_users_db}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG,  # might break here
        reload=False,  # set to True
    )
