@echo off
REM Zombie Quest launcher (Windows). Requires Python 3.9+ on PATH.

python -c "import pygame" 2>NUL
if errorlevel 1 (
    echo Installing pygame...
    pip install -r requirements.txt
)

echo Starting Zombie Quest: Neon Dead - Minneapolis '82...
python main.py
