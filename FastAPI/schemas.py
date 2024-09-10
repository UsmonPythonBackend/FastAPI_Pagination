from pydantic import BaseModel
from typing import Optional

class RegisterSchema(BaseModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]

class LoginSchema(BaseModel):
    username_or_email: Optional[str]
    password: Optional[str]

class PasswordReset(BaseModel):
    password: Optional[str]
    confirm_password: Optional[str]

class CreatePost(BaseModel):
    image_path: Optional[str]
    caption: Optional[str]

class PostListModel(BaseModel):
    id: Optional[int]
    image_path: Optional[str]
    caption: Optional[str]
class PostUpdateModel(BaseModel):
    image_path: Optional[str]
    caption: Optional[str]

class LikesCreateModel(BaseModel):
    user_id: Optional[str]
    post_id: Optional[str]


class LikesModel(BaseModel):
    user_id: Optional[str]
    post_id: Optional[str]
class LikesUpdateModel(BaseModel):
    user_id: Optional[str]
    post_id: Optional[str]

class CommentsCreateModel(BaseModel):
    user_id: Optional[str]
    post_id: Optional[str]
class CommentsUpdateModel:
    user_id: Optional[str]
    post_id: Optional[str]


class FollowersModel(BaseModel):
    follower_id: Optional[str]
    following_id: Optional[str]
class FollowersCreateModel(BaseModel):
    follower_id: Optional[str]
    following_id: Optional[str]
class FollowersUpdateModel(BaseModel):
    follower_id: Optional[str]
    following_id: Optional[str]



class Settings(BaseModel):
    authjwt_secret_key: str = "79b82e0018828fd0ccf4209e36700d98eaae41f1250ddf9ace0a826f9adcf940"

