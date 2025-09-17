#!/bin/bash

# Ensure pygame is available
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install pygame
fi

echo "Starting Zombie Quest - SCI Edition..."
python3 main.py
