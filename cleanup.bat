@echo off
echo ==================================================
echo   VERSIGHT AI - DEEP CLEANUP UTILITY
echo ==================================================
echo.
echo [1/3] Terminating all Python processes...
taskkill /F /IM python.exe /T 2>nul

echo [2/3] Terminating all Node.js processes...
taskkill /F /IM node.exe /T 2>nul

echo [3/3] Clearing ghost instances on ports 8010 and 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8010 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo.
echo [DONE] System memory is now clean.
echo You can now run "node start" to begin a fresh session.
echo.
pause
