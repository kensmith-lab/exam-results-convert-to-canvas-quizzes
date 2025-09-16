#!/bin/bash

# Enhanced Canvas QTI Generator - Folder Processing
echo "🚀 Enhanced Canvas QTI Generator - Multi-Format Support"
echo "======================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install enhanced dependencies
echo "📦 Installing enhanced dependencies..."
pip3 install -r requirements.txt

# Check if folder path provided as argument
if [ "$1" ]; then
    echo "🔄 Processing folder: $1"
    python3 generate_qti_enhanced.py "$1"
else
    echo "🔄 Processing documents/ folder..."
    python3 generate_qti_enhanced.py
fi

echo ""
echo "✅ Process completed!"
echo "📁 Check the output/ folder for your QTI zip file."