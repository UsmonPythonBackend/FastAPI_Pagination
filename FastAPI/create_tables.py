from models import User, Post, Comments, Likes, Tags, PostTags, Followers, Messages
from database import engine, Base

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)