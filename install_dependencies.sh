#!/bin/bash

echo "========================================"
echo "   FIXORA PRO - Dependency Installer"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python found. Checking version..."
python3 --version

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.8+ is required"
    echo "Current version:"
    python3 --version
    exit 1
fi

echo
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
fi

echo
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "========================================"
echo "   Installation Completed Successfully!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit config.py with your API keys"
echo "2. Run: python main_realtime.py"
echo "3. Or run: python bot_interface/telegram_bot.py for bot only"
echo
echo "To activate the virtual environment in the future:"
echo "source .venv/bin/activate"
echo
