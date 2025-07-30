#!/bin/bash

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    # Try pip first, fall back to system package
    if command -v pip3 &> /dev/null; then
        pip3 install pygame --user
    else
        sudo apt update && sudo apt install -y python3-pygame
    fi
fi

# Run the game
echo "Starting 1950's Zombie Quest - Enhanced Edition..."
echo "Note: In headless environments, the game will run a demo and exit automatically."
python3 zombie_quest.py