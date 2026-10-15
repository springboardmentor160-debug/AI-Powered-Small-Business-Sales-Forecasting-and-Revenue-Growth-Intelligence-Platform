@echo off
call "%~dp0.venv\Scripts\activate.bat"
cd /d "%~dp0backend"
uvicorn main:app --reload --port 8000
