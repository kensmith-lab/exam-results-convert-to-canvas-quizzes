#!/bin/bash

# Canvas QTI Generator - S3 Edition
echo "🚀 Canvas QTI Generator - S3 Edition"
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Setting up configuration..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your S3 configuration:"
    echo "   - S3_BUCKET_NAME: Your S3 bucket name"
    echo "   - AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY: Your AWS credentials"
    echo "   - Or AWS_PROFILE: Your AWS CLI profile name"
    echo ""
    echo "Then run this script again!"
    exit 1
fi

# Load environment variables
source .env

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Run the S3 generator
echo ""
echo "🔄 Running S3 QTI Generator..."
python3 generate_qti_s3.py

echo ""
echo "✅ Process completed!"