#!/bin/bash
echo "========================================"
echo "  Deepak AI Assistant - Setup"
echo "========================================"
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Installation failed. Trying with pip3..."
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting Deepak AI..."
python app.py
