#!/bin/bash

# Quick Start Script for RAG Chatbot
# This script sets up and starts the chatbot in one go

echo "========================================================================"
echo "RAG Chatbot - Quick Start"
echo "========================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "========================================================================"
    echo "OpenAI API Key Setup"
    echo "========================================================================"
    echo ""
    echo "You need an OpenAI API key to use this chatbot."
    echo "Get one at: https://platform.openai.com/api-keys"
    echo ""
    
    python3 setup_openai.py
    echo ""
fi

# Check if database exists and has data
if [ ! -f "chatbot.db" ]; then
    echo "========================================================================"
    echo "Initializing Knowledge Base"
    echo "========================================================================"
    echo ""
    echo "Adding sample knowledge entries..."
    python3 seed_knowledge.py
    echo ""
fi

# Start the server
echo "========================================================================"
echo "Starting Server"
echo "========================================================================"
echo ""
python3 start.py

