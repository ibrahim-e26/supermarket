"""
models/inventory.py — Audit log for stock movements
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class MovementType(str, enum.Enum):
    restock = "restock"
    sale = "sale"
    adjustment = "adjustment"
    return_ = "return"


class InventoryLog(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType, name="movement_type"), nullable=False)
    change_qty = Column(Float, nullable=False)   # positive = stock in, negative = stock out
    before_qty = Column(Float, nullable=True)
    after_qty = Column(Float, nullable=True)
    reference_id = Column(Integer, nullable=True)  # sale_id or restock doc id
    reason = Column(String(200), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
