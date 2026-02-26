"""
models/customer.py — CRM customer record
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    email = Column(String(120), unique=True, nullable=True)
    credit_limit = Column(Float, default=0.0)
    outstanding_credit = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
