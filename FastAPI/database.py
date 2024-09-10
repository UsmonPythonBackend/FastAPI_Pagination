from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('postgresql://postgres:123@localhost:5432/instagram', echo=True)
Base = declarative_base()
Session = sessionmaker()
