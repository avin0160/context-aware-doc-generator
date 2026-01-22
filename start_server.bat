@echo off
echo ============================================================
echo  Fast Documentation Generator Server
echo ============================================================
echo.
echo Starting server (this will take 1-2 minutes to load models)...
echo.
echo The browser will open automatically when ready.
echo.
echo Server URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

start /B python repo_fastapi_server.py

echo Waiting for server to start...
timeout /t 60 /nobreak > nul

start http://localhost:8000

echo.
echo Server should be running now!
echo Check the browser or go to: http://localhost:8000
echo.
pause
