#!/bin/bash

# GitHub Profile README Stats Setup Script
# Run this script to test your setup locally

echo "🚀 GitHub Profile Stats Setup Test"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check if required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set. Please set this environment variable."
    echo "   export GITHUB_TOKEN='your_github_token'"
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo "⚠️  GITHUB_USERNAME not set. Please set this environment variable."
    echo "   export GITHUB_USERNAME='your_github_username'"
fi

if [ -z "$LEETCODE_USERNAME" ]; then
    echo "ℹ️  LEETCODE_USERNAME not set (optional)."
fi

if [ -z "$HACKERRANK_USERNAME" ]; then
    echo "ℹ️  HACKERRANK_USERNAME not set (optional)."
fi

# Install requirements
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if README.md exists
if [ ! -f "README.md" ]; then
    echo "❌ README.md not found in current directory."
    exit 1
fi

echo "✅ README.md found"

# Check if the Python script exists
if [ ! -f "scripts/update_readme.py" ]; then
    echo "❌ scripts/update_readme.py not found."
    exit 1
fi

echo "✅ Python script found"

# Test the script if environment variables are set
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_USERNAME" ]; then
    echo ""
    echo "🧪 Testing the stats collection script..."
    python3 scripts/update_readme.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Script executed successfully!"
        echo "📝 Check your README.md file for updated stats."
    else
        echo "❌ Script failed. Check the error messages above."
    fi
else
    echo ""
    echo "⏭️  Skipping script test - environment variables not set."
fi

echo ""
echo "🎉 Setup test completed!"
echo "📖 Read SETUP_GUIDE.md for detailed setup instructions."