@echo off
REM Safe server startup script for Windows
echo ===================================================================
echo   Context-Aware Documentation Generator - Safe Start
echo ===================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate venv and run diagnostic
echo [1/3] Running diagnostic test...
echo.
venv\Scripts\python.exe test_server_startup.py
if errorlevel 1 (
    echo.
    echo ERROR: Diagnostic test failed!
    echo Please fix the errors above before starting the server.
    pause
    exit /b 1
)

echo.
echo ===================================================================
echo   Diagnostic passed! Starting server...
echo ===================================================================
echo.

REM Start server
echo [2/3] Starting FastAPI server...
echo.
echo Server will start on: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
pause

echo [3/3] Launching server...
venv\Scripts\python.exe repo_fastapi_server.py

echo.
echo Server stopped.
pause
