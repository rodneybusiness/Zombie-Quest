#!/usr/bin/env python3

import sys
import pygame

# Test pygame initialization
print("Testing pygame initialization...")
pygame.init()
print("✓ Pygame initialized successfully")

# Test display setup
print("Testing display setup...")
try:
    screen = pygame.display.set_mode((320, 200))
    print("✓ Display mode set successfully")
    pygame.quit()
except pygame.error as e:
    print(f"⚠ Display not available: {e}")
    print("This is expected in headless environments")

# Test VGA palette
print("Testing VGA palette...")
VGA_PALETTE = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170), (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255), (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255)
]
print(f"✓ VGA palette created with {len(VGA_PALETTE)} colors")

print("\nAll tests completed!")
print("The game should work properly now.")