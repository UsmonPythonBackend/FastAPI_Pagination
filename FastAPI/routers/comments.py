from fastapi import APIRouter, status, Depends, HTTPException, Query
from models import Post, User, Comments
from database import engine, Session
from fastapi.encoders import jsonable_encoder
from schemas import CommentsCreateModel, CommentsUpdateModel
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, paginate, add_pagination

session = Session(bind=engine)


comment_router = APIRouter(prefix="/comments", tags=["Comments"])




@comment_router.get('/', response_model=Page)
async def get_comment():
    all_comments = session.query(Comments).all()
    return jsonable_encoder(paginate(all_comments))


add_pagination(comment_router)




@comment_router.get("/")
async def get_comments(Authorization: AuthJWT = Depends(AuthJWT)):
    try:
        Authorization.jwt_required()
        current_user = session.query(User).filter(User.username == Authorization.get_jwt_subject()).first()
        comments = session.query(Comments).filter(Post.user == current_user).all()
        return jsonable_encoder(comments)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")


@comment_router.post("/")
async def create_comment(comment: CommentsCreateModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        check_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
        if check_user:
            new_comment = Comments(
                user_id=check_user.id,
                post_id=comment.post_id
            )
            session.add(new_comment)
            session.commit()
            data = {
                "success": True,
                "code": 201,
                "message": "Created comment successfully"
            }
            return jsonable_encoder(data)
        return {"success": False, "code": 400, "message": "Bad Request"}

    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")





@comment_router.put("/{id}")
async def update_comment(id: int, comment: CommentsUpdateModel, Authorization: AuthJWT = Depends()):
    try:
        Authorization.jwt_required()
        check_user = session.query(User).filter(User.username == Authorization.get_jwt_subject()).first()
        if check_user:
            check_post = session.query(Post).filter(Post.id == id).first()
            if check_post:
                for key, value in comment.dict().items():
                    setattr(check_post, key, value)

                    data = {
                        "code": 200,
                        "success": True,
                        "message": "Successfully updated comment",
                        "object": {
                            "user_id": check_user.id,
                            "post_id": comment.post_id,
                        }
                    }
                    session.add(check_post)
                    session.commit()
                    return jsonable_encoder(data)

            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')


@comment_router.delete("/{id}")
async def delete_comment(id: int, Authorization: AuthJWT = Depends()):
    try:
        Authorization.jwt_required()
        check_user = session.query(User).filter(User.username == Authorization.get_jwt_subject()).first()
        if check_user:
            comment = session.query(Comments).filter(Comments.id == id).first()
            if comment:
                session.delete(comment)
                session.commit()
                return jsonable_encoder({"code": 200, "message": "Successfully deleted comment"})
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')