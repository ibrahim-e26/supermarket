from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventoryRestockRequest(BaseModel):
    product_id: int
    qty: float
    reason: Optional[str] = "Restock"


class InventoryLogResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    change_qty: float
    before_qty: Optional[float]
    after_qty: Optional[float]
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
