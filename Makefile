.PHONY: run backend frontend

run:
	@echo "Note: Windows users might prefer 'python run.py' or 'run.bat'"
	@make -j 2 backend frontend

backend:
	uvicorn backend.main:app --reload --port 8000

frontend:
	streamlit run frontend/app.py
