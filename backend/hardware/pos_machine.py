"""
hardware/pos_machine.py — Pine Labs Plutus Smart POS terminal integration.

Pine Labs Plutus Smart terminals expose a local HTTP API when running on the
same network. The terminal listens on a configurable host:port.

Configure via .env:
    PINE_LABS_HOST=192.168.1.200
    PINE_LABS_PORT=8080
    PINE_LABS_MERCHANT_ID=your_merchant_id
    PINE_LABS_TERMINAL_ID=your_terminal_id

Reference: Pine Labs Plutus Smart Local API (PSDK)
    - POST /GetCloudBasedTxn to initiate
    - GET  /GetCloudBasedTxn/{reference} to poll status
"""
import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

HOST = os.getenv("PINE_LABS_HOST", "192.168.1.200")
PORT = os.getenv("PINE_LABS_PORT", "8080")
MERCHANT_ID = os.getenv("PINE_LABS_MERCHANT_ID", "")
TERMINAL_ID = os.getenv("PINE_LABS_TERMINAL_ID", "")
BASE_URL = f"http://{HOST}:{PORT}"

# Payment type codes used by Pine Labs
PAYMENT_TYPE_CODES = {
    "card": "4001",   # Debit/Credit card
    "upi": "4002",    # UPI
    "emi": "4009",    # EMI
}


def initiate_payment(amount: float, payment_mode: str = "card", reference: str = None) -> dict:
    """
    Send a payment request to the Pine Labs Plutus terminal.

    Args:
        amount: Amount in INR (float, e.g. 149.50)
        payment_mode: "card" | "upi"
        reference: Optional bill reference string

    Returns:
        {"success": bool, "transaction_id": str, "status": str, "message": str}
    """
    amount_paise = int(round(amount * 100))  # Pine Labs expects paise (integer)
    txn_type_code = PAYMENT_TYPE_CODES.get(payment_mode, "4001")

    payload = {
        "MerchantID": MERCHANT_ID,
        "TerminalID": TERMINAL_ID,
        "TransactionType": int(txn_type_code),
        "Amount": amount_paise,
        "BillingRefNo": reference or f"SALE-{int(time.time())}",
        "MerchantName": os.getenv("STORE_NAME", "E26 Supermarket"),
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/GetCloudBasedTxn",
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Pine Labs initiate response: {data}")

        return {
            "success": True,
            "transaction_id": data.get("PlutusTransactionReferenceID", ""),
            "status": "initiated",
            "message": "Payment request sent to POS terminal",
            "raw": data,
        }

    except requests.exceptions.ConnectionError:
        logger.warning("Pine Labs terminal not reachable")
        return {
            "success": False,
            "transaction_id": None,
            "status": "error",
            "message": f"Cannot connect to POS terminal at {BASE_URL}",
        }
    except Exception as e:
        logger.error(f"Pine Labs error: {e}")
        return {"success": False, "transaction_id": None, "status": "error", "message": str(e)}


def get_payment_status(transaction_id: str) -> dict:
    """
    Poll the Pine Labs terminal for the result of a transaction.

    Returns:
        {"status": "success"|"failed"|"pending", "transaction_id": str, "message": str}
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/GetCloudBasedTxn/{transaction_id}",
            params={"MerchantID": MERCHANT_ID, "TerminalID": TERMINAL_ID},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Pine Labs status response: {data}")

        response_code = str(data.get("ResponseCode", ""))
        if response_code == "00":
            status = "success"
        elif response_code in ("", "null"):
            status = "pending"
        else:
            status = "failed"

        return {
            "status": status,
            "transaction_id": transaction_id,
            "response_code": response_code,
            "message": data.get("ResponseMessage", ""),
            "card_type": data.get("CardType", ""),
            "approval_code": data.get("ApprovalCode", ""),
            "raw": data,
        }

    except Exception as e:
        logger.error(f"Pine Labs status check error: {e}")
        return {"status": "error", "transaction_id": transaction_id, "message": str(e)}
