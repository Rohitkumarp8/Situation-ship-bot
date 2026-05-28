from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    looking_for = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    photo_file_id = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    is_profile_complete = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    from_user_id = Column(BigInteger, nullable=False)
    to_user_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActiveChat(Base):
    __tablename__ = "active_chats"

    id = Column(Integer, primary_key=True)
    user1_id = Column(BigInteger, nullable=False)
    user2_id = Column(BigInteger, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
