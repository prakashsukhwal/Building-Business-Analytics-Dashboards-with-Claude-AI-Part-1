@echo off
start cmd /k "venv\Scripts\activate && uvicorn api:app --reload --port 8000"
start cmd /k "venv\Scripts\activate && streamlit run streamlit_app.py"