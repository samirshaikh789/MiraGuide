@echo off
echo Starting MiraGuide Backend...
echo.
echo Backend will run at: http://127.0.0.1:8787
echo API docs available at: http://127.0.0.1:8787/docs
echo.
cd /d "%~dp0backend_new"
uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
