import os
import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends, Query

from database import Session, engine
from models import User
from schemas import RegisterSchema, LoginSchema, PasswordReset
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from fastapi_pagination import Page, paginate, add_pagination




load_dotenv()
session = Session(bind=engine)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get('/', response_model=Page)
async def get_users():
    all_users = session.query(User).all()
    return jsonable_encoder(paginate(all_users))

add_pagination(auth_router)




@auth_router.get("/")
async def auth_page(request: AuthJWT = Depends()):
    try:
        request.jwt_required()
        return {"message": "Welcome auth"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")


@auth_router.post("/register")
async def register(user: RegisterSchema):
    check_user = session.query(User).filter(User.username == user.username).first()
    if check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()
    data = {
        "status": 201,
        "message": "User created successfully",
        "object": {
            "username": user.username,
            "email": user.email,
            "password": generate_password_hash(user.password)
        }
    }
    return jsonable_encoder(data)

@auth_router.post("/login")
async def login(request: LoginSchema, authorization: AuthJWT = Depends()):
    check_user = session.query(User).filter(
        or_(
            User.username == request.username_or_email,
            User.email == request.username_or_email,
        )).first()
    if check_user and check_password_hash(check_user.password, request.password):
        access_token = authorization.create_access_token(subject=request.username_or_email, expires_time=datetime.timedelta(minutes=int(os.getenv("time_access"))))
        refresh_token = authorization.create_refresh_token(subject=request.username_or_email, expires_time=datetime.timedelta(days=int(os.getenv("time_refresh"))))
        data = {
            "success": True,
            "code": 200,
            "message": "Login successful",
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token
            },
        }
        return jsonable_encoder(data)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")



@auth_router.get('/users')
async def get_users():
    users = session.query(User).all()
    return jsonable_encoder(users)


@auth_router.get('/login/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        access_lifetime = datetime.timedelta(minutes=1)
        refresh_lifetime = datetime.timedelta(days=3)
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        check_user = session.query(User).filter(User.username == current_user).first()
        if check_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        new_access_token = Authorize.create_access_token(subject=check_user.username, expires_time=access_lifetime)

        response = {
            "code": 200,
            "success": True,
            "message": "New refresh token created",
            "data": new_access_token
        }
        return jsonable_encoder(response)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@auth_router.get('/reset-password')
async def reset_password(user: PasswordReset, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        if user.password == user.confirm_password:
            current_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
            if current_user:
                current_user.password = generate_password_hash(user.password)
                session.add(current_user)
                session.commit()

                data = {
                    "code": 200,
                    "success": True,
                    "message": "Password reset"
                }
                return jsonable_encoder(data)
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")