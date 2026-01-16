@echo off
REM Startup script for Context-Aware Documentation Generator
REM Author: team-8
REM System: charvaka

echo.
echo ========================================
echo Context-Aware Documentation Generator
echo Author: team-8
echo System: charvaka
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the FastAPI server
echo Starting FastAPI server...
python repo_fastapi_server.py

pause
