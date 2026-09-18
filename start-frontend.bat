@echo off
echo Starting MiraGuide Frontend...
echo.
echo Frontend will run at: http://localhost:5173
echo.
cd /d "%~dp0frontend"
npm run dev
