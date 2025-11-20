@echo off
REM Quick Start Script for RAG Chatbot (Windows)

echo ========================================================================
echo RAG Chatbot - Quick Start
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed
    echo   Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo √ Python found
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo √ Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo √ Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo √ Dependencies installed
echo.

REM Check if .env exists
if not exist ".env" (
    echo ========================================================================
    echo OpenAI API Key Setup
    echo ========================================================================
    echo.
    echo You need an OpenAI API key to use this chatbot.
    echo Get one at: https://platform.openai.com/api-keys
    echo.
    
    python setup_openai.py
    echo.
)

REM Check if database exists
if not exist "chatbot.db" (
    echo ========================================================================
    echo Initializing Knowledge Base
    echo ========================================================================
    echo.
    echo Adding sample knowledge entries...
    python seed_knowledge.py
    echo.
)

REM Start the server
echo ========================================================================
echo Starting Server
echo ========================================================================
echo.
python start.py

pause

