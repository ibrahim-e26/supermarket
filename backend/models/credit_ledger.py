"""
models/credit_ledger.py — Credit sales and repayments tracker
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base


class CreditLedger(Base):
    __tablename__ = "credit_ledger"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    entry_type = Column(String(20), default="debit")  # 'debit' (owed) | 'credit' (paid)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=True)
    notes = Column(String(300), nullable=True)
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    sale = relationship("Sale")
