@echo off
echo ========================================
echo   Deepak AI Assistant - Setup
echo ========================================
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed. Make sure Python is installed.
    pause
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo.
echo Starting Deepak AI...
python app.py
pause
