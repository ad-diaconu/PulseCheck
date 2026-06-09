from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from logger_setup import LOGGING_CONFIG, setup_logging
from passlib.context import CryptContext
from pydantic import BaseModel

# pass lib.context : password hashing and verification
# jwt ( PyJWT ) : creating and veryfing JSON web tokens

logger = setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# symmetric key config
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

# main object used for password hashing ( not jwt hashing )
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

fake_users_db = {}


class UserAuth(BaseModel):
    email: str
    password: str


# helper fn
def create_jwt(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=1)
    # to_encode.update({"exp":expire,"iat":now,"iss":"pulsechcek"})
    to_encode.update({"exp": expire})
    # symmetric sygning
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt(request: Request):
    # Extract the token from the HttpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        logger.warning(f"JWT Verification failed: No token provided")
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f" JWT Verification successful for user: {payload.get('sub')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT Verification failed: Token expired.")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        logger.warning("JWT Verification failed: Invalid token.")
        raise HTTPException(status_code=401, detail="Invalid token")


# endpoints
@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserAuth):
    if user.email in fake_users_db:
        logger.warning(f"Signup failed: Email {user.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt).decode("utf-8")
    fake_users_db[user.email] = {
        "email": user.email,
        "hashed_password": hashed_password,
    }

    logger.info(f"New user registered: {user.email}")
    return {"message": "User created successfully"}


@app.post("/login")
def login(user: UserAuth, response: Response):
    db_user = fake_users_db.get(user.email)

    if not db_user:
        logger.warning(f"Login failed: User {user.email} not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    is_valid = bcrypt.checkpw(
        user.password.encode("utf-8"), db_user["hashed_password"].encode("utf-8")
    )

    if not db_user or not is_valid:
        logger.warning(f"Login failed: Invalid credentials for {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # client creates the jwt
    jwt_token = create_jwt({"sub": user.email, "role": "standard_user"})

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,  # js cant read this ( prevents XSS )
        secure=False,  # set true in produuction
        samesite="lax",  # protects against CSRF
    )

    logger.info(f"User logged in successfully: {user.email}")
    return {"message": "Login successfull"}


@app.get("/me")
def get_protected_profile(payload: dict = Depends(verify_jwt)):
    logger.info(f"User {payload.get('sub')} accessed protected profile route.")
    return {
        "message": "Accessed secure data.",
        "your_email": payload.get("sub"),
        "your_role": payload.get("role"),
    }


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    logger.info("User logged out.")
    return {"message": "Logged out"}


@app.get("/users")
def get_unprotected_users():
    logger.info("Accessed unprotected users list.")
    return {"users": fake_users_db}


@app.get("/protected-users")
def get_users(payload: dict = Depends(verify_jwt)):
    logger.info(f"User {payload.get('sub')} accessed users list.")
    return {"users": fake_users_db}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG,  # might break here
        reload=False,  # set to True
    )
