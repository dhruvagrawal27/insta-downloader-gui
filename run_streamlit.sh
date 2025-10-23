#!/bin/bash

# Instagram Downloader - Streamlit Deployment Script

echo "🚀 Starting Instagram Downloader Web Application..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements_streamlit.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

echo "✅ Dependencies installed successfully!"

# Create downloads directory
mkdir -p downloads

echo "📁 Created downloads directory"

# Ask user which version to run
echo ""
echo "Which version would you like to run?"
echo "1) Single URL Downloader"
echo "2) Batch URL Downloader"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🌐 Starting Single URL Downloader..."
        streamlit run streamlit_app.py
        ;;
    2)
        echo "🌐 Starting Batch URL Downloader..."
        streamlit run streamlit_batch_app.py
        ;;
    *)
        echo "❌ Invalid choice. Starting Single URL Downloader..."
        streamlit run streamlit_app.py
        ;;
esac
