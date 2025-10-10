@echo off
:: Video Archive Tool - Phase 2 Development Launcher
:: Yambo Studio - With Scene Detection and Full Processing

cd /d "%~dp0"

:: Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

:: Run Phase 2 application
python src/main_phase2.py

:: Deactivate venv
deactivate

pause
