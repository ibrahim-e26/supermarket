@echo off
echo Starting Supermarket POS + CRM System...

echo Starting FastAPI Backend...
start "Supermarket Backend" cmd /k "uvicorn backend.main:app --reload --port 8000"

echo Starting Streamlit Frontend...
start "Supermarket Frontend" cmd /k "streamlit run frontend/app.py"

echo Both services started in separate windows!
