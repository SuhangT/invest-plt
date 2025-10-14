@echo off
chcp 65001 >nul
echo ========================================
echo Investment Portfolio System - Startup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check virtual environment
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
if not exist "venv\Lib\site-packages\flask\" (
    echo [INFO] Installing backend dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Initialize database
if not exist "backend\invest.db" (
    echo [INFO] Initializing database...
    python backend\init_db.py
    if errorlevel 1 (
        echo [ERROR] Failed to initialize database
        pause
        exit /b 1
    )
)

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js not found, frontend cannot start
    echo [INFO] Please visit https://nodejs.org/ to install Node.js
    echo.
    echo [INFO] Starting backend only...
    python backend\app.py
    pause
    exit /b 0
)

REM Install frontend dependencies
if not exist "frontend\node_modules\" (
    echo [INFO] Installing frontend dependencies (this may take a few minutes)...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ========================================
echo [SUCCESS] Environment ready
echo ========================================
echo.
echo [INFO] Starting backend service (port 5000)...
echo [INFO] Starting frontend service (port 3000)...
echo.
echo Please visit: http://localhost:3000
echo.
echo Press Ctrl+C to stop services
echo ========================================
echo.

REM Start backend (background)
start "Backend Service" cmd /k "venv\Scripts\activate.bat && python backend\app.py"

REM Wait 2 seconds for backend to start
timeout /t 2 /nobreak >nul

REM Start frontend
cd frontend
call npm start

pause
