"""
models/user.py — System user (Admin / Staff)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from backend.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.staff, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
