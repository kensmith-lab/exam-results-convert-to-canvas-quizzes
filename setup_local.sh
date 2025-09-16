#!/bin/bash

# Canvas QTI Generator - Local Project Setup
echo "🚀 Setting up Canvas QTI Generator"
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Python detected: $python_version"
else
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    mkdir output
    echo "✅ Created output directory"
fi

# Create documents directory if it doesn't exist  
if [ ! -d "documents" ]; then
    mkdir documents
    echo "✅ Created documents directory"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
chmod +x run_generator.sh
chmod +x run_s3_generator.sh
echo "✅ Made scripts executable"

# Test with sample files
echo ""
echo "🧪 Testing with sample documents..."
python3 generate_qti.py

echo ""
echo "🎉 Local project setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add your exam documents to the 'documents/' folder"
echo "2. Run: ./run_generator.sh"
echo "3. Import the generated .zip file to Canvas"
echo ""
echo "📁 Project structure:"
echo "├── documents/          # Place your exam files here"  
echo "├── output/            # Generated QTI files"
echo "├── generate_qti.py    # Local generator"
echo "├── run_generator.sh   # Quick launcher"
echo "└── requirements.txt   # Dependencies"