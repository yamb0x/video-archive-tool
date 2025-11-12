@echo off
REM Social Media Prep Tool - Launch Script
REM Yambo Studio

echo.
echo ========================================
echo  Social Media Prep Tool
echo  Yambo Studio
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python
)

echo.
echo Starting application...
echo.

REM Run the application
python src\main_social.py

REM Check for errors
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo  ERROR: Application crashed
    echo ========================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Application closed successfully
echo.
pause
