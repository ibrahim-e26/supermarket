"""
routers/sales.py — Create and retrieve sales
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.sales_service import SalesService
from backend.services.auth_service import get_current_user
from backend.schemas.sale import SaleCreate, SaleResponse
from backend.models.user import User

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SalesService.create_sale(db, data, user_id=current_user.id)


@router.get("/", response_model=List[SaleResponse])
def list_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return SalesService.get_sales(db, skip, limit)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return SalesService.get_sale_by_id(db, sale_id)


@router.patch("/{sale_id}/payment-status")
def update_payment(
    sale_id: int,
    status: str,
    ref: str = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Called by POS machine callback to confirm/fail a card payment."""
    return SalesService.update_payment_status(db, sale_id, status, ref)
