#!/bin/bash

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame
fi

# Run the fixed game
echo "Starting Zombie Quest VGA..."
python3 main.py