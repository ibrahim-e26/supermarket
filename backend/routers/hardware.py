"""
routers/hardware.py — Endpoints that proxy to hardware modules.
Backend calls these; frontend calls backend (no hardware import in frontend).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.auth_service import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/hardware", tags=["Hardware"])


# ── Weight reading ────────────────────────────────────────────────────────────

@router.get("/scale")
def get_weight(_: User = Depends(get_current_user)):
    """Read current weight from the RS-232 digital scale."""
    from backend.hardware.scale import read_weight
    return read_weight()


# ── Receipt printing ──────────────────────────────────────────────────────────

class PrintRequest(BaseModel):
    sale_id: int
    cashier: str
    customer: Optional[str] = None
    created_at: str
    payment_mode: str
    transaction_ref: Optional[str] = None
    items: list
    subtotal: float
    discount: float = 0.0
    tax: float = 0.0
    total: float


@router.post("/print")
def print_receipt_endpoint(data: PrintRequest, _: User = Depends(get_current_user)):
    """Format and send receipt to thermal printer."""
    from backend.hardware.printer import print_receipt
    result = print_receipt(data.model_dump())
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Print failed"))
    return result


# ── POS Machine ───────────────────────────────────────────────────────────────

class PaymentRequest(BaseModel):
    amount: float
    payment_mode: str = "card"
    reference: Optional[str] = None


@router.post("/payment/initiate")
def initiate_pos_payment(data: PaymentRequest, _: User = Depends(get_current_user)):
    """Send a payment request to the Pine Labs Plutus Smart terminal."""
    from backend.hardware.pos_machine import initiate_payment
    return initiate_payment(data.amount, data.payment_mode, data.reference)


@router.get("/payment/status/{transaction_id}")
def get_pos_payment_status(transaction_id: str, _: User = Depends(get_current_user)):
    """Poll the Pine Labs terminal for transaction result."""
    from backend.hardware.pos_machine import get_payment_status
    return get_payment_status(transaction_id)
