@echo off
chcp 65001 >nul
title JARVIS Mark LV
color 0B

echo.
echo   J . A . R . V . I . S
echo   Starting...
echo.

cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo   JARVIS wurde beendet oder ein Fehler ist aufgetreten.
    echo   Fuehre install.bat aus falls noch nicht geschehen.
    echo.
    pause
)
