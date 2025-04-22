@echo off
cd /d "C:\Users\fhnaz\Desktop\AZ-scan"
echo Activating virtual environment...
call "%CD%\.venv\Scripts\activate.bat"

if errorlevel 1 (
    echo Failed to activate the virtual environment.
    pause
    exit /b
)

echo Running script...
python main.py

echo Done.
pause