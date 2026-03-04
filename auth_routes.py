from datetime import timedelta, datetime

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from database import session, engine
from models import User
from schemas import SignUpModel, LoginModel, Settings

auth_router = APIRouter(
    prefix="/auth",
)

session = session(bind=engine)
conf = Settings()


def create_token(subject: str, expires_delta: timedelta, token_type: str):
    to_encode = {
        "sub": subject,
        "exp": datetime.utcnow() + expires_delta,
        "type": token_type
    }
    return jwt.encode(to_encode, conf.authjwt_secret_key, algorithm="HS256")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, conf.authjwt_secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Only access token is allowed")
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token not valid")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token is expired")

    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@auth_router.get("/")
async def protected_route(username: str = Depends(get_current_user)):
    return {
        "message": "Siz himoyalangan sahifaga kirdingiz",
        "user": username
    }


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


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user: LoginModel):
    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = create_token(db_user.username, timedelta(minutes=30), "access")
        refresh_token = create_token(db_user.username, timedelta(days=7), "refresh")

        tokens = {
            "access": access_token,
            "refresh": refresh_token,
        }
        response = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "Login success",
            "data": tokens
        }
        return jsonable_encoder(response)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect username or password"
    )


@auth_router.get("/login/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, conf.authjwt_secret_key, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Faqat refresh token qabul qilinadi")
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token yaroqsiz")
        db_user = session.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=401, detail="User with this username already exists")
        new_access_token = create_token(db_user.username, timedelta(minutes=30), "access")
        new_refresh_token = create_token(db_user.username, timedelta(days=7), "refresh")
        tokens = {
            "access": new_access_token,
            "refresh": new_refresh_token,
        }
        response = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "New access token created successfully",
            "data": tokens
        }
        return jsonable_encoder(response)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
