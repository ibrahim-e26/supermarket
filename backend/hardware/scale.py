"""
hardware/scale.py — RS-232 Digital Scale via pyserial.

Connects to a serial weighing scale (common protocol: send ENQ, read weight string).
Most generic RS-232 supermarket scales respond with a string like "  1.250 kg\r\n".

Configure via .env:
    SCALE_COM_PORT=COM3
    SCALE_BAUD_RATE=9600
    SCALE_TIMEOUT=2
"""
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

COM_PORT = os.getenv("SCALE_COM_PORT", "COM3")
BAUD_RATE = int(os.getenv("SCALE_BAUD_RATE", 9600))
TIMEOUT = float(os.getenv("SCALE_TIMEOUT", 2))


def read_weight() -> dict:
    """
    Open the serial port, read a weight value, and return it.

    Returns:
        {"weight": float, "unit": "kg", "raw": str}  on success
        {"weight": None, "error": str}                on failure
    """
    try:
        import serial  # pyserial
    except ImportError:
        return {"weight": None, "error": "pyserial not installed. Run: pip install pyserial"}

    try:
        with serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT,
        ) as ser:
            # Some scales need ENQ to trigger a reading
            ser.write(b"\x05")

            raw = ser.readline().decode("ascii", errors="ignore").strip()
            logger.info(f"Scale raw response: {repr(raw)}")

            return _parse_weight(raw)

    except Exception as e:
        logger.warning(f"Scale read error: {e}")
        return {"weight": None, "error": str(e)}


def _parse_weight(raw: str) -> dict:
    """Parse a weight string like '  1.250 kg' or 'ST,GS,  1.500kg' ."""
    match = re.search(r"(\d+\.?\d*)\s*(kg|g|lb)?", raw, re.IGNORECASE)
    if not match:
        return {"weight": None, "error": f"Could not parse scale response: {repr(raw)}"}

    value = float(match.group(1))
    unit = (match.group(2) or "kg").lower()

    # Convert grams to kg if needed
    if unit == "g":
        value = value / 1000
        unit = "kg"

    return {"weight": round(value, 3), "unit": unit, "raw": raw}
