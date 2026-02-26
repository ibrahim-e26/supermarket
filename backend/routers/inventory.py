"""
routers/inventory.py — Stock management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.inventory_service import InventoryService
from backend.services.auth_service import get_current_user, require_admin
from backend.schemas.inventory import InventoryRestockRequest, InventoryLogResponse
from backend.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/restock", response_model=InventoryLogResponse)
def restock(
    data: InventoryRestockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return InventoryService.restock(db, data, user_id=current_user.id)


@router.get("/logs", response_model=List[InventoryLogResponse])
def get_logs(
    product_id: Optional[int] = Query(None),
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return InventoryService.get_logs(db, product_id=product_id, limit=limit)


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return InventoryService.get_low_stock(db)
