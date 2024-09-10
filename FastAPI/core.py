from fastapi import FastAPI, Depends, status, HTTPException, Query
from routers.posts import post_router
from routers.auth import auth_router
from routers.likes import likes_router
from routers.comments import comment_router
from routers.followers import followers_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from database import Session, engine
from models import User, Post, Likes, Followers,Comments
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_

app = FastAPI()

session = Session(bind=engine)
@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(post_router)
app.include_router(auth_router)
app.include_router(likes_router)
app.include_router(followers_router)
app.include_router(comment_router)




@app.get("/")
def root():
    return {"msg": "Welcome"}


@app.get('/{username}')
async def get_user_page(username: str, authorization: AuthJWT = Depends()):
    try:
        authorization.jwt_required()
        current_user = session.query(User).filter(
            or_(
                User.username == authorization.get_jwt_subject(),
                User.email == authorization.get_jwt_subject()
            )
        ).first()
        if current_user:
            other_user = session.query(User).filter(User.username == username).first()
            if other_user:
                data = {
                    "success": True,
                    "code": 200,
                    "message": f"{other_user.username} profile page"
                }
                return jsonable_encoder(data)

            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{username} not found")

        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{username} not found")

    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")