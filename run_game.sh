#!/bin/bash

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame
fi

# Clear any cached Python files
echo "Clearing Python cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Run the fixed game
echo "Starting 1950's Zombie Quest - Enhanced Edition (Fixed)..."
echo "Running: zombie_quest_fixed.py"
python3 zombie_quest_fixed.py