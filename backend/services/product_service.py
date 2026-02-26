"""
services/product_service.py — CRUD operations for products.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.product import Product
from backend.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200) -> List[Product]:
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return p

    @staticmethod
    def get_by_barcode(db: Session, barcode: str) -> Product:
        p = db.query(Product).filter(Product.barcode == barcode).first()
        if not p:
            raise HTTPException(status_code=404, detail=f"No product with barcode {barcode}")
        return p

    @staticmethod
    def search(db: Session, query: str) -> List[Product]:
        pattern = f"%{query}%"
        return (
            db.query(Product)
            .filter(
                (Product.name.ilike(pattern)) |
                (Product.barcode.ilike(pattern)) |
                (Product.category.ilike(pattern))
            )
            .limit(50)
            .all()
        )

    @staticmethod
    def create(db: Session, data: ProductCreate) -> Product:
        # Check barcode uniqueness
        if data.barcode:
            existing = db.query(Product).filter(Product.barcode == data.barcode).first()
            if existing:
                raise HTTPException(status_code=400, detail="Barcode already exists")
        product = Product(**data.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update(db: Session, product_id: int, data: ProductUpdate) -> Product:
        product = ProductService.get_by_id(db, product_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: int) -> dict:
        product = ProductService.get_by_id(db, product_id)
        db.delete(product)
        db.commit()
        return {"message": f"Product {product_id} deleted"}

    @staticmethod
    def get_low_stock(db: Session) -> List[Product]:
        return (
            db.query(Product)
            .filter(Product.stock_qty <= Product.min_stock_alert)
            .all()
        )
