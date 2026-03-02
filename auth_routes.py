from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime

from sqlalchemy.sql.functions import user

from schemas import SignUpModel, LoginModel, Settings
from database import session, engine
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt, JWTError
from sqlalchemy import or_

auth_router = APIRouter(
    prefix="/auth",
)

session = session(bind=engine)
conf = Settings()


def create_token(subject: str, expires_delta: timedelta):
    to_encode = {"sub": subject, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(to_encode, conf.authjwt_secret_key, algorithm="HS256")


@auth_router.get("/")
async def signup():
    return {"message": "Bu auth route signup sahifasi"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(new_user)
    session.commit()

    model = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "is_staff": new_user.is_staff,
    }
    response_model = {
        "success": True,
        "code": status.HTTP_201_CREATED,
        "message": "User is created successfully",
        "data": model,
    }
    return response_model


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(loginModel: LoginModel):
    # db_user = session.query(User).filter(User.username == loginModel.username).first()
    db_user = session.query(User).filter(or_(User.username == loginModel.username_or_email,
                                             User.email == loginModel.username_or_email)).first()

    if db_user and check_password_hash(db_user.password, loginModel.password):
        access_token = create_token(db_user.username, timedelta(minutes=30))
        refresh_token = create_token(db_user.username, timedelta(days=7))

        token = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        response = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Logged in successfully",
            "data": token,
        }

        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")


@auth_router.get("/login/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, conf.authjwt_secret_key, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        db_user = session.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        new_access_token = create_token(db_user.username, timedelta(minutes=30))

        return {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Token refreshed successfully",
            "data": {
                "access_token": new_access_token
            }
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )




