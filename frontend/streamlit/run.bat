@echo off
REM COMMIT 12: Streamlit Frontend Launcher
REM Script pour démarrer l'interface Streamlit

echo.
echo ====================================
echo EduGuide - Streamlit Frontend
echo ====================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Installer les dépendances
echo Installing dependencies...
pip install -r requirements.txt -q

REM Lancer Streamlit
echo.
echo Starting Streamlit app on http://localhost:8501
echo Press Ctrl+C to stop
echo.

streamlit run app.py --logger.level=info

pause
