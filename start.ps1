# PowerShell Startup Script for Context-Aware Documentation Generator
# Author: team-8
# System: charvaka

Write-Host ""
Write-Host "========================================"
Write-Host "Context-Aware Documentation Generator"
Write-Host "Author: team-8"
Write-Host "System: charvaka"
Write-Host "========================================"
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Start the FastAPI server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
python repo_fastapi_server.py
