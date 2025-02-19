from fastapi import APIRouter, status, HTTPException, Depends, Query
import json
from database import engine, Session
from models import Post, User
from fastapi.encoders import jsonable_encoder
from schemas import CreatePost, PostUpdateModel
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from fastapi import FastAPI
from fastapi_pagination import Page, paginate, add_pagination

session = Session(bind=engine)

post_router = APIRouter(prefix="/posts", tags=["Posts"])



@post_router.get('/', response_model=Page)
async def get_users():
    all_posts = session.query(Post).all()
    return jsonable_encoder(paginate(all_posts))

add_pagination(post_router)


@post_router.get("/")
async def get_posts(authorization: AuthJWT = Depends()):
    try:
        authorization.jwt_required()
        current_user = session.query(User).filter(
            or_(
                User.username == authorization.get_jwt_subject(),
                User.email == authorization.get_jwt_subject()
            )
        ).first()
        if current_user:
            posts = session.query(Post).filter(Post.user == current_user).all()
            return jsonable_encoder(posts)
    except HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@post_router.post("/")
async def create_post(post: CreatePost, authorization: AuthJWT = Depends()):
    try:
        authorization.jwt_required()
        current_user = session.query(User).filter(
            or_(
                User.username == authorization.get_jwt_subject(),
                User.email == authorization.get_jwt_subject()
            )
        ).first()
        if current_user:
            new_post = Post(
                image_path=post.image_path,
                caption=post.caption
            )
            new_post.user = current_user
            session.add(new_post)
            session.commit()
            data = {
                "status": 201,
                "message": f"Post created successfully by {authorization.get_jwt_subject()}"
            }
            return jsonable_encoder(data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")



@post_router.put("/{id}")
async def update_post(id: int, post: PostUpdateModel, authorization: AuthJWT = Depends()):
    try:
        authorization.jwt_required()
        current_user = session.query(User).filter(User.username == authorization.get_jwt_subject()).first()
        if current_user:
            update_post = session.query(Post).filter(Post.id == id).first()
            if update_post:
                for key, value in post.dict().items():
                    setattr(update_post, key, value)

                    data = {
                        "code": 200,
                        "success": True,
                        "message": "Successfully updated post",
                        "object": {
                            "caption": update_post.caption,
                            "user_id": update_post.id,
                            "image_path": update_post.image_path,
                        }
                    }
                    session.add(update_post)
                    session.commit()
                    return jsonable_encoder(data)

            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')


@post_router.delete("/{id}")
async def delete_post(id: int, authorization: AuthJWT = Depends()):
    try:
        authorization.jwt_required()
        current_user = session.query(User).filter(User.username == authorization.get_jwt_subject()).first()
        if current_user:
            post = session.query(Post).filter(Post.id == id).first()
            if post:
                session.delete(post)
                session.commit()
                return jsonable_encoder({"code": 200, "message": "Successfully deleted post"})
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')
