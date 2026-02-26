"""
hardware/printer.py — Epson Thermal Receipt Printer via python-escpos.

Supports USB (default) and Network printers.
Configure via .env:
    PRINTER_TYPE=usb       # or 'network'
    PRINTER_VENDOR_ID=0x04b8
    PRINTER_PRODUCT_ID=0x0202
    # For network:
    PRINTER_HOST=192.168.1.100
    PRINTER_PORT=9100

    STORE_NAME=E26 Supermarket
    STORE_ADDRESS=123 Main Street
    STORE_PHONE=+91-9999999999
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

STORE_NAME = os.getenv("STORE_NAME", "E26 Supermarket")
STORE_ADDRESS = os.getenv("STORE_ADDRESS", "")
STORE_PHONE = os.getenv("STORE_PHONE", "")
PRINTER_TYPE = os.getenv("PRINTER_TYPE", "usb")


def _get_printer():
    """Return a connected printer object or raise RuntimeError."""
    try:
        from escpos.printer import Usb, Network
    except ImportError:
        raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")

    if PRINTER_TYPE == "network":
        host = os.getenv("PRINTER_HOST", "192.168.1.100")
        port = int(os.getenv("PRINTER_PORT", 9100))
        return Network(host, port)
    else:
        vendor_id = int(os.getenv("PRINTER_VENDOR_ID", "0x04b8"), 16)
        product_id = int(os.getenv("PRINTER_PRODUCT_ID", "0x0202"), 16)
        return Usb(vendor_id, product_id)


def format_receipt(sale_data: dict) -> list:
    """
    Build a list of print commands from sale data dict.
    sale_data structure:
        {
          "sale_id": int,
          "created_at": str,
          "cashier": str,
          "customer": str | None,
          "payment_mode": str,
          "transaction_ref": str | None,
          "items": [{"name", "qty", "unit_price", "subtotal"}, ...],
          "subtotal": float,
          "discount": float,
          "tax": float,
          "total": float,
        }
    """
    lines = []
    lines.append(("header", STORE_NAME))
    if STORE_ADDRESS:
        lines.append(("text", STORE_ADDRESS))
    if STORE_PHONE:
        lines.append(("text", STORE_PHONE))
    lines.append(("separator", "="))
    lines.append(("text", f"Receipt #: {sale_data.get('sale_id', 'N/A')}"))
    lines.append(("text", f"Date     : {sale_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}"))
    lines.append(("text", f"Cashier  : {sale_data.get('cashier', '-')}"))
    if sale_data.get("customer"):
        lines.append(("text", f"Customer : {sale_data['customer']}"))
    lines.append(("separator", "-"))

    for item in sale_data.get("items", []):
        name = item["name"][:22]
        qty = item["qty"]
        price = item["unit_price"]
        sub = item["subtotal"]
        lines.append(("item", f"{name:<22} {qty}x{price:.2f}  {sub:.2f}"))

    lines.append(("separator", "-"))
    lines.append(("text", f"{'Subtotal':.<30} {sale_data.get('subtotal', 0):.2f}"))
    if sale_data.get("discount", 0) > 0:
        lines.append(("text", f"{'Discount':.<30}-{sale_data['discount']:.2f}"))
    if sale_data.get("tax", 0) > 0:
        lines.append(("text", f"{'Tax':.<30} {sale_data['tax']:.2f}"))
    lines.append(("bold", f"{'TOTAL':.<30} {sale_data.get('total', 0):.2f}"))
    lines.append(("separator", "-"))
    lines.append(("text", f"Payment  : {sale_data.get('payment_mode', 'cash').upper()}"))
    if sale_data.get("transaction_ref"):
        lines.append(("text", f"Ref      : {sale_data['transaction_ref']}"))
    lines.append(("separator", "="))
    lines.append(("center", "Thank you for shopping!"))
    lines.append(("center", "Visit again :)"))
    lines.append(("cut", None))
    return lines


def print_receipt(sale_data: dict) -> dict:
    """Format and send receipt to the printer."""
    try:
        printer = _get_printer()
        commands = format_receipt(sale_data)

        for cmd_type, content in commands:
            if cmd_type == "header":
                printer.set(align="center", bold=True, double_height=True, double_width=True)
                printer.text(content + "\n")
                printer.set()  # reset
            elif cmd_type == "center":
                printer.set(align="center")
                printer.text(content + "\n")
                printer.set()
            elif cmd_type == "bold":
                printer.set(bold=True)
                printer.text(content + "\n")
                printer.set()
            elif cmd_type == "separator":
                printer.text(content * 42 + "\n")
            elif cmd_type == "item":
                printer.text(content + "\n")
            elif cmd_type == "text":
                printer.text(content + "\n")
            elif cmd_type == "cut":
                printer.cut()

        return {"success": True, "message": "Receipt printed successfully"}

    except Exception as e:
        logger.error(f"Printer error: {e}")
        return {"success": False, "error": str(e)}
