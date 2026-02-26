"""
routers/products.py — Product CRUD and barcode lookup
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.product_service import ProductService
from backend.services.auth_service import get_current_user, require_admin
from backend.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from backend.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProductService.get_all(db, skip, limit)


@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., description="Search query (name, barcode, or category)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProductService.search(db, q)


@router.get("/low-stock", response_model=List[ProductResponse])
def low_stock(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return ProductService.get_low_stock(db)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProductService.get_by_barcode(db, barcode)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProductService.get_by_id(db, product_id)


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return ProductService.create(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return ProductService.update(db, product_id, data)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return ProductService.delete(db, product_id)
