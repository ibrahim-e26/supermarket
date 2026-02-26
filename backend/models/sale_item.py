"""
models/sale_item.py — Line items inside a sale
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from backend.database import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(150))          # snapshot at time of sale
    qty = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)       # per-item discount %
    tax = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)    # (unit_price * qty) - discount + tax

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")
