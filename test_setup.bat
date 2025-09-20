@echo off
REM GitHub Profile README Stats Setup Script for Windows
REM Run this script to test your setup locally

echo 🚀 GitHub Profile Stats Setup Test
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Check if required environment variables are set
if "%GITHUB_TOKEN%"=="" (
    echo ⚠️  GITHUB_TOKEN not set. Please set this environment variable.
    echo    set GITHUB_TOKEN=your_github_token
)

if "%GITHUB_USERNAME%"=="" (
    echo ⚠️  GITHUB_USERNAME not set. Please set this environment variable.
    echo    set GITHUB_USERNAME=your_github_username
)

if "%LEETCODE_USERNAME%"=="" (
    echo ℹ️  LEETCODE_USERNAME not set ^(optional^).
)

if "%HACKERRANK_USERNAME%"=="" (
    echo ℹ️  HACKERRANK_USERNAME not set ^(optional^).
)

REM Install requirements
echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Check if README.md exists
if not exist "README.md" (
    echo ❌ README.md not found in current directory.
    pause
    exit /b 1
)

echo ✅ README.md found

REM Check if the Python script exists
if not exist "scripts\update_readme.py" (
    echo ❌ scripts\update_readme.py not found.
    pause
    exit /b 1
)

echo ✅ Python script found

REM Test the script if environment variables are set
if not "%GITHUB_TOKEN%"=="" if not "%GITHUB_USERNAME%"=="" (
    echo.
    echo 🧪 Testing the stats collection script...
    python scripts\update_readme.py
    
    if %errorlevel% equ 0 (
        echo ✅ Script executed successfully!
        echo 📝 Check your README.md file for updated stats.
    ) else (
        echo ❌ Script failed. Check the error messages above.
    )
) else (
    echo.
    echo ⏭️  Skipping script test - environment variables not set.
)

echo.
echo 🎉 Setup test completed!
echo 📖 Read SETUP_GUIDE.md for detailed setup instructions.
pause