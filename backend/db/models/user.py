
from sqlalchemy import Column, Integer,TEXT
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id  = Column(Integer,primary_key=True,index=True)
    username =Column(TEXT,nullable=False)
    email = Column(TEXT,unique=True,index=True,nullable=False)
    cognito_sub = Column(TEXT,unique=True,nullable=False,index=True)



