# 🛒 E26 Supermarket POS + CRM System

A full-stack **Point-of-Sale and CRM system** built with **FastAPI**, **Streamlit**, and **PostgreSQL**, with hardware integrations for barcode scanner, digital scale, thermal printer, and Pine Labs POS machine.

---

## 📁 Project Structure

```
Supermarket/
├── .env                        ← Your environment variables
├── .env.example                ← Template
├── requirements.txt
│
├── backend/
│   ├── main.py                 ← FastAPI entry point
│   ├── database.py             ← SQLAlchemy engine + session
│   │
│   ├── models/                 ← ORM models (7 tables)
│   │   ├── user.py, product.py, customer.py
│   │   ├── sale.py, sale_item.py
│   │   ├── inventory.py, credit_ledger.py
│   │
│   ├── schemas/                ← Pydantic request/response models
│   │   ├── user.py, product.py, customer.py
│   │   ├── sale.py, inventory.py
│   │
│   ├── services/               ← Business logic layer
│   │   ├── auth_service.py     ← JWT + bcrypt auth
│   │   ├── product_service.py
│   │   ├── sales_service.py    ← Atomic sale creation
│   │   ├── inventory_service.py
│   │   └── dashboard_service.py
│   │
│   ├── routers/                ← FastAPI endpoint routers
│   │   ├── auth.py, products.py, sales.py
│   │   ├── inventory.py, dashboard.py, hardware.py
│   │
│   └── hardware/               ← Hardware integration layer
│       ├── barcode.py          ← Zebra DS2208 (HID keyboard)
│       ├── scale.py            ← RS-232 serial scale (pyserial)
│       ├── printer.py          ← Epson ESC/POS (python-escpos)
│       └── pos_machine.py      ← Pine Labs Plutus Smart HTTP API
│
└── frontend/
    ├── app.py                  ← Streamlit entry point + navigation
    ├── login.py                ← Login page
    ├── pos.py                  ← POS billing interface
    ├── inventory.py            ← Admin inventory management
    └── dashboard.py            ← Admin analytics dashboard
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally
- Create database: `CREATE DATABASE supermarket_crm;`

### 2. Install dependencies
```powershell
cd "c:\Users\Lenovo\Documents\Razik\E26\Supermarket"
pip install -r requirements.txt
```

### 3. Configure environment
Edit `.env` with your PostgreSQL credentials and hardware settings.

### 4. Run the application
You can run both the frontend and backend together using one of these methods:

- **Windows Batch Script:** Double-click `run.bat` or run `.\run.bat` in your terminal.
- **Python Script:** Run `python run.py`. This is the best way to handle stopping both services with `Ctrl+C`.
- **Makefile:** If you have `make` installed, run `make run`.

Alternatively, you can run them manually in separate terminals:

**Start the backend:**
```powershell
uvicorn backend.main:app --reload --port 8000
```
- API docs: http://localhost:8000/docs
- Tables are **auto-created** on first run
- Default admin: `admin` / `admin123` (**change immediately!**)

**Start the frontend:**
```powershell
streamlit run frontend/app.py
```
- Opens at: http://localhost:8501

---

## 🔐 Default Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | `admin`  | `admin123` |

> ⚠️ **Change the default password after first login via the API.**

---

## 🔌 Hardware Setup

| Device | Connection | Config Key |
|--------|-----------|------------|
| Zebra DS2208 | USB (HID keyboard) | No config needed |
| Digital Scale | RS-232 Serial | `SCALE_COM_PORT` |
| Epson Printer | USB or Network | `PRINTER_TYPE`, `PRINTER_HOST` |
| Pine Labs Plutus | Local HTTP | `PINE_LABS_HOST`, `PINE_LABS_PORT` |

> Hardware modules gracefully handle missing connections — the system works without hardware in dev mode.

---

## 📊 API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Login, get JWT |
| POST | `/auth/register` | Create user |
| GET  | `/products/` | List products |
| GET  | `/products/barcode/{code}` | Barcode lookup |
| POST | `/products/` | Add product (admin) |
| PUT  | `/products/{id}` | Edit product (admin) |
| DELETE | `/products/{id}` | Delete product (admin) |
| POST | `/sales/` | Create sale |
| GET  | `/sales/` | List sales |
| POST | `/inventory/restock` | Restock (admin) |
| GET  | `/dashboard/summary` | Daily KPIs |
| GET  | `/dashboard/top-products` | Top sellers |
| GET  | `/hardware/scale` | Read scale weight |
| POST | `/hardware/print` | Print receipt |
| POST | `/hardware/payment/initiate` | Start POS payment |
