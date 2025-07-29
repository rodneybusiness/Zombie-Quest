#!/bin/bash

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame
fi

# Run the game
echo "Starting 1950's Zombie Quest - Enhanced Edition..."
python3 zombie_quest.py