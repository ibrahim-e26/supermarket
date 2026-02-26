"""
hardware/barcode.py — Zebra DS2208 barcode scanner helper.

The Zebra DS2208 operates as a USB HID keyboard device — it requires no driver.
When a barcode is scanned, the device types the barcode string followed by Enter.

In the Streamlit UI, we use a standard text_input field with on_change to capture
the scanned value. This module provides utility functions for parsing / cleaning
the raw scanned string received from the UI.
"""
import re


def clean_barcode(raw: str) -> str:
    """Strip whitespace, carriage returns, and non-printable characters from a scanned string."""
    if not raw:
        return ""
    cleaned = raw.strip().replace("\r", "").replace("\n", "")
    # Keep only printable ASCII characters
    cleaned = re.sub(r"[^\x20-\x7E]", "", cleaned)
    return cleaned.strip()


def is_valid_barcode(barcode: str) -> bool:
    """Basic validation: must be 4–20 alphanumeric characters."""
    if not barcode:
        return False
    return bool(re.match(r"^[A-Za-z0-9\-]{4,20}$", barcode))
