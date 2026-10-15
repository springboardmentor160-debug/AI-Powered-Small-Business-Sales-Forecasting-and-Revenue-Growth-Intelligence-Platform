@echo off
REM One-time setup (Windows CMD, Python 3.11). Run from the project root:  setup_windows.bat
py -3.11 -m venv .venv || (echo Python 3.11 not found. Install it from python.org and tick "Add to PATH". & exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-backend.txt || exit /b 1
pip install -r requirements.txt || echo WARNING: ML libraries failed to install (often prophet). The API and dashboard still work; ML scripts fall back to scikit-learn.
if not exist backend\.env copy backend\.env.example backend\.env
cd backend && python init_db.py && python load_data.py && cd ..
cd frontend && call npm install && cd ..
echo.
echo Setup done. Edit backend\.env (SECRET_KEY, ADMIN_PASSWORD) if you like, then run start_backend.bat and start_frontend.bat.
