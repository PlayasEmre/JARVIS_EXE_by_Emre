@echo off
chcp 65001 >nul
title JARVIS Mark LV - Installation
color 0B

echo.
echo   ============================================
echo      J . A . R . V . I . S   Mark LV
echo      Installation - by FatihMakes
echo   ============================================
echo.

:: Check Python
echo   [1/4] Python wird geprueft...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Python wurde nicht gefunden!
    echo   Bitte installiere Python 3.11 oder 3.12:
    echo   https://www.python.org/downloads/
    echo.
    echo   WICHTIG: Setze den Haken bei "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   Python %%v gefunden.
echo.

:: Install dependencies
echo   [2/4] Abhaengigkeiten werden installiert...
echo   (Das kann ein paar Minuten dauern)
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo   Fehler bei der Installation!
    echo   Versuche es nochmal oder pruefe die Fehlermeldung.
    pause
    exit /b 1
)
echo.
echo   Abhaengigkeiten installiert.
echo.

:: Setup Playwright browsers
echo   [3/4] Browser fuer Web-Suche werden installiert...
python -m playwright install chromium >nul 2>&1
echo   Browser installiert.
echo.

:: API Key
echo   [4/4] Konfiguration
echo.

if not exist "config" mkdir config

:: Check if api_keys.json exists and has a real key
set "NEEDS_KEY=1"
if exist "config\api_keys.json" (
    findstr /c:"gemini_api_key" "config\api_keys.json" >nul 2>&1
    if not errorlevel 1 (
        findstr /c:"DEIN_GEMINI_API_KEY_HIER" "config\api_keys.json" >nul 2>&1
        if errorlevel 1 (
            set "NEEDS_KEY=0"
            echo   API-Key bereits konfiguriert.
        )
    )
)

if "%NEEDS_KEY%"=="1" (
    echo   Du brauchst einen Gemini API-Key (kostenlos).
    echo   Hol dir einen hier: https://aistudio.google.com/apikey
    echo.
    set /p "API_KEY=  Gemini API-Key eingeben: "
    set /p "USER_NAME=  Dein Name: "

    (
        echo {
        echo     "gemini_api_key": "%API_KEY%",
        echo     "os_system": "windows",
        echo     "user_name": "%USER_NAME%",
        echo     "dashboard_pin": "JARVIS"
        echo }
    ) > "config\api_keys.json"
    echo.
    echo   Konfiguration gespeichert.
)

echo.
echo   ============================================
echo      Installation abgeschlossen!
echo.
echo      Starte JARVIS mit:  start.bat
echo   ============================================
echo.
pause
