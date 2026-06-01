from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone


# pass lib.context : password hashing and verification
# jwt ( PyJWT ) : creating and veryfing JSON web tokens
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# symmetric key config
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

# main object used for password hashing ( not jwt hashing )
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {}

class UserAuth(BaseModel):
    email: str
    password: str

# helper fn
def create_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp":expire})
    # symmetric sygning
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt(request: Request):
    # Extract the token from the HttpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# endpoints
@app.post("/signup",status_code=status.HTTP_201_CREATED)
def signup(user: UserAuth):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    fake_users_db[user.email] = {"email":user.email,"hashed_password":hashed_password}
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: UserAuth, response: Response):
    db_user = fake_users_db.get(user.email)

    if not db_user or not pwd_context.verify(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # client creates the jwt
    jwt_token = create_jwt({"sub":user.email, 'role':"standard_user"})

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True, # js cant read this ( prevents XSS )
        secure=False, # set true in produuction
        samesite="lax" # protects against CSRF
    )
    return {"message":"Login successfull"}


