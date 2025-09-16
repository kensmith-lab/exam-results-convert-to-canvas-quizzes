#!/bin/bash

# Canvas QTI Generator Launcher
echo "🚀 Canvas QTI Generator"
echo "========================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install beautifulsoup4 PyPDF2 python-docx lxml

# Run the generator
echo "🔄 Generating QTI files..."
python3 generate_qti.py

echo "✅ Done! Check the output/ folder for your QTI zip file."