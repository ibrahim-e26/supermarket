from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    credit_limit: float = 0.0


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    credit_limit: Optional[float] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    credit_limit: float
    outstanding_credit: float
    created_at: datetime

    class Config:
        from_attributes = True
