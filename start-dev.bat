@echo off
REM SmartQuiz Local Development Startup Script (Windows)

echo.
echo 🚀 SmartQuiz Local Development Setup
echo =====================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.11 or later
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✓ Dependencies installed

REM Create .env file if it doesn't exist
echo.
echo Checking environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo ✓ Created .env from .env.example
    echo ⚠️  Please update .env with your configuration
) else (
    echo ✓ .env file exists
)

REM Check database
echo.
echo Checking MySQL connection...
python -c "
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'admin@123')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    print(f'✓ Database connected - MySQL {version[0]}')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" || (
    echo ERROR: Database connection failed
    echo Make sure MySQL is running and credentials are correct in .env
    exit /b 1
)

REM Start application
echo.
echo Starting SmartQuiz application...
echo ✓ Application starting on http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py
