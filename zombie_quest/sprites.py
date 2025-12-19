"""Advanced pixel art sprite generation - creates stunning, detailed character graphics.

This module generates high-quality pixel art sprites programmatically, featuring:
- Detailed 16x32 pixel characters with proper anatomy and shading
- Multiple animation frames with smooth motion
- Character-specific details (clothing, hair, accessories)
- Dynamic lighting and color palettes
- Zombie variants with unique visual traits
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import pygame
import math
import random

Color = Tuple[int, int, int]
ColorAlpha = Tuple[int, int, int, int]


def blend_colors(c1: Color, c2: Color, ratio: float) -> Color:
    """Blend two colors together."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * ratio),
        int(c1[1] + (c2[1] - c1[1]) * ratio),
        int(c1[2] + (c2[2] - c1[2]) * ratio),
    )


def shade_color(color: Color, factor: float) -> Color:
    """Shade a color (factor < 1 = darker, > 1 = lighter)."""
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )


def add_highlight(color: Color, amount: int = 40) -> Color:
    """Add highlight to color."""
    return (
        min(255, color[0] + amount),
        min(255, color[1] + amount),
        min(255, color[2] + amount),
    )


class HeroPalette:
    """Color palette for the hero character - 80s punk rocker."""
    # Skin tones with shading
    SKIN = (255, 210, 180)
    SKIN_SHADOW = (220, 170, 140)
    SKIN_HIGHLIGHT = (255, 235, 215)

    # Big 80s hair - deep purple/violet
    HAIR = (60, 20, 80)
    HAIR_SHADOW = (40, 10, 55)
    HAIR_HIGHLIGHT = (90, 40, 120)

    # Purple leather jacket
    JACKET = (100, 40, 130)
    JACKET_SHADOW = (70, 25, 95)
    JACKET_HIGHLIGHT = (140, 70, 170)
    JACKET_ACCENT = (180, 100, 200)  # Studs/details

    # Band t-shirt underneath
    SHIRT = (30, 30, 35)
    SHIRT_DESIGN = (200, 50, 100)  # Neon pink band logo

    # Tight dark jeans
    PANTS = (35, 35, 50)
    PANTS_SHADOW = (25, 25, 35)
    PANTS_HIGHLIGHT = (50, 50, 70)

    # Boots
    BOOTS = (25, 20, 30)
    BOOTS_BUCKLE = (180, 160, 100)

    # Accessories
    EARRING = (255, 215, 0)  # Gold
    WRISTBAND = (200, 50, 50)


class ZombiePalette:
    """Color palettes for zombie types."""

    @staticmethod
    def get_palette(zombie_type: str) -> Dict[str, Color]:
        palettes = {
            "scene": {  # Record store zombie
                "skin": (120, 160, 120),
                "skin_shadow": (90, 130, 90),
                "skin_highlight": (150, 190, 150),
                "clothes": (70, 50, 90),
                "clothes_shadow": (50, 35, 65),
                "clothes_highlight": (95, 70, 120),
                "hair": (80, 100, 80),
                "eyes": (200, 255, 180),
                "blood": (100, 60, 60),
            },
            "bouncer": {  # Security zombie
                "skin": (110, 150, 110),
                "skin_shadow": (80, 120, 80),
                "skin_highlight": (140, 180, 140),
                "clothes": (25, 25, 35),  # Black suit
                "clothes_shadow": (15, 15, 25),
                "clothes_highlight": (40, 40, 55),
                "hair": (30, 35, 30),
                "eyes": (180, 255, 160),
                "blood": (90, 50, 50),
                "shades": (20, 20, 25),  # Sunglasses
            },
            "rocker": {  # Band member zombie
                "skin": (130, 170, 130),
                "skin_shadow": (100, 140, 100),
                "skin_highlight": (160, 200, 160),
                "clothes": (120, 30, 40),  # Band tee
                "clothes_shadow": (85, 20, 30),
                "clothes_highlight": (160, 50, 65),
                "hair": (220, 200, 150),  # Bleached
                "eyes": (220, 255, 200),
                "blood": (110, 70, 70),
            },
            "dj": {  # Radio DJ zombie
                "skin": (125, 165, 125),
                "skin_shadow": (95, 135, 95),
                "skin_highlight": (155, 195, 155),
                "clothes": (50, 50, 75),
                "clothes_shadow": (35, 35, 55),
                "clothes_highlight": (70, 70, 100),
                "hair": (45, 50, 55),
                "eyes": (190, 255, 170),
                "blood": (95, 55, 55),
                "headphones": (60, 60, 70),
            },
        }
        return palettes.get(zombie_type, palettes["scene"])


def create_detailed_hero_sprite(direction: str, frame: int, size: Tuple[int, int] = (16, 32)) -> pygame.Surface:
    """Create a beautifully detailed pixel art hero sprite."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = HeroPalette

    # Animation variables
    walk_bob = [0, -1, 0, -1][frame % 4]
    leg_phase = [0, 1, 2, 1][frame % 4]
    arm_swing = [0, 1, 2, 1][frame % 4]
    hair_flow = [-1, 0, 1, 0][frame % 4]

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    if direction == "down":
        # === FRONT VIEW ===

        # BOOTS (with buckles)
        boot_y = h - 4
        left_boot_x = 4 + (1 if leg_phase == 1 else -1 if leg_phase == 3 else 0)
        right_boot_x = 10 + (-1 if leg_phase == 1 else 1 if leg_phase == 3 else 0)

        draw_rect(left_boot_x, boot_y, 3, 4, p.BOOTS)
        draw_rect(right_boot_x, boot_y, 3, 4, p.BOOTS)
        draw_pixel(left_boot_x + 1, boot_y + 1, p.BOOTS_BUCKLE)
        draw_pixel(right_boot_x + 1, boot_y + 1, p.BOOTS_BUCKLE)

        # LEGS/JEANS
        leg_y = h - 10
        draw_rect(4, leg_y, 3, 6, p.PANTS)
        draw_rect(9, leg_y, 3, 6, p.PANTS)
        draw_pixel(4, leg_y + 1, p.PANTS_SHADOW)
        draw_pixel(9, leg_y + 1, p.PANTS_SHADOW)
        draw_pixel(6, leg_y + 2, p.PANTS_HIGHLIGHT)
        draw_pixel(11, leg_y + 2, p.PANTS_HIGHLIGHT)

        # JACKET BODY
        jacket_y = h - 18 + walk_bob
        draw_rect(3, jacket_y, 10, 8, p.JACKET)
        # Lapels
        draw_rect(4, jacket_y, 2, 5, p.JACKET_HIGHLIGHT)
        draw_rect(10, jacket_y, 2, 5, p.JACKET_HIGHLIGHT)
        # Center opening showing shirt
        draw_rect(6, jacket_y + 1, 4, 4, p.SHIRT)
        # Band logo on shirt
        draw_pixel(7, jacket_y + 2, p.SHIRT_DESIGN)
        draw_pixel(8, jacket_y + 2, p.SHIRT_DESIGN)
        draw_pixel(7, jacket_y + 3, p.SHIRT_DESIGN)
        # Studs on jacket
        for i in range(3):
            draw_pixel(4 + i * 4, jacket_y + 6, p.JACKET_ACCENT)

        # ARMS
        left_arm_y = h - 16 + arm_swing
        right_arm_y = h - 16 - arm_swing + 1
        # Left arm
        draw_rect(1, left_arm_y, 2, 6, p.JACKET)
        draw_pixel(1, left_arm_y, p.JACKET_HIGHLIGHT)
        draw_rect(1, left_arm_y + 5, 2, 2, p.SKIN)
        draw_pixel(1, left_arm_y + 4, p.WRISTBAND)
        # Right arm
        draw_rect(13, right_arm_y, 2, 6, p.JACKET)
        draw_pixel(14, right_arm_y, p.JACKET_HIGHLIGHT)
        draw_rect(13, right_arm_y + 5, 2, 2, p.SKIN)
        draw_pixel(14, right_arm_y + 4, p.WRISTBAND)

        # HEAD
        head_y = h - 24 + walk_bob
        # Face shape
        draw_rect(5, head_y, 6, 6, p.SKIN)
        # Jaw shading
        draw_rect(5, head_y + 4, 1, 2, p.SKIN_SHADOW)
        draw_rect(10, head_y + 4, 1, 2, p.SKIN_SHADOW)
        # Cheek highlights
        draw_pixel(6, head_y + 2, p.SKIN_HIGHLIGHT)

        # EYES
        draw_pixel(6, head_y + 2, (50, 50, 60))  # Left eye
        draw_pixel(9, head_y + 2, (50, 50, 60))  # Right eye
        draw_pixel(6, head_y + 2, (255, 255, 255))  # Eye highlight
        draw_pixel(9, head_y + 2, (255, 255, 255))

        # NOSE and MOUTH hints
        draw_pixel(7, head_y + 3, p.SKIN_SHADOW)
        draw_pixel(8, head_y + 4, p.SKIN_SHADOW)

        # BIG 80s HAIR
        hair_y = head_y - 5 + walk_bob
        # Main volume
        draw_rect(3 + hair_flow, hair_y, 10, 6, p.HAIR)
        # Side volume (teased)
        draw_rect(2, hair_y + 1, 2, 4, p.HAIR)
        draw_rect(12, hair_y + 1, 2, 4, p.HAIR)
        # Top spikes/volume
        draw_rect(4, hair_y - 1, 2, 2, p.HAIR)
        draw_rect(8, hair_y - 1, 3, 2, p.HAIR)
        # Highlights
        draw_pixel(5, hair_y + 1, p.HAIR_HIGHLIGHT)
        draw_pixel(9, hair_y + 1, p.HAIR_HIGHLIGHT)
        draw_pixel(6, hair_y, p.HAIR_HIGHLIGHT)
        # Shadows
        draw_pixel(3, hair_y + 3, p.HAIR_SHADOW)
        draw_pixel(12, hair_y + 3, p.HAIR_SHADOW)

        # EARRING
        draw_pixel(4, head_y + 3, p.EARRING)

    elif direction == "up":
        # === BACK VIEW ===

        boot_y = h - 4
        draw_rect(4, boot_y, 3, 4, p.BOOTS)
        draw_rect(10, boot_y, 3, 4, p.BOOTS)

        leg_y = h - 10
        draw_rect(4, leg_y, 3, 6, p.PANTS)
        draw_rect(9, leg_y, 3, 6, p.PANTS)

        jacket_y = h - 18 + walk_bob
        draw_rect(3, jacket_y, 10, 8, p.JACKET)
        # Back details
        draw_rect(5, jacket_y + 1, 6, 5, p.JACKET_SHADOW)
        # Studs on back
        draw_pixel(5, jacket_y + 6, p.JACKET_ACCENT)
        draw_pixel(10, jacket_y + 6, p.JACKET_ACCENT)

        # Arms
        draw_rect(1, h - 16 - arm_swing, 2, 6, p.JACKET)
        draw_rect(13, h - 16 + arm_swing, 2, 6, p.JACKET)

        # Head from back
        head_y = h - 24 + walk_bob
        draw_rect(5, head_y, 6, 6, p.SKIN)

        # Hair from back (even bigger)
        hair_y = head_y - 5 + walk_bob
        draw_rect(2, hair_y, 12, 8, p.HAIR)
        draw_rect(3, hair_y - 1, 4, 2, p.HAIR)
        draw_rect(9, hair_y - 1, 3, 2, p.HAIR)
        draw_pixel(6, hair_y, p.HAIR_HIGHLIGHT)
        draw_pixel(10, hair_y + 1, p.HAIR_HIGHLIGHT)

    elif direction == "left":
        # === LEFT SIDE VIEW ===

        boot_y = h - 4
        boot_x = 6 + (leg_phase - 1)
        draw_rect(boot_x, boot_y, 4, 4, p.BOOTS)
        draw_pixel(boot_x + 2, boot_y + 1, p.BOOTS_BUCKLE)

        leg_y = h - 10
        draw_rect(5, leg_y, 4, 6, p.PANTS)
        draw_pixel(5, leg_y + 1, p.PANTS_SHADOW)
        draw_pixel(7, leg_y + 3, p.PANTS_HIGHLIGHT)

        jacket_y = h - 18 + walk_bob
        draw_rect(4, jacket_y, 6, 8, p.JACKET)
        draw_rect(8, jacket_y + 1, 2, 4, p.JACKET_HIGHLIGHT)
        draw_pixel(5, jacket_y + 6, p.JACKET_ACCENT)

        # Arm (coming forward)
        arm_x = 3 - arm_swing
        draw_rect(arm_x, h - 15, 3, 5, p.JACKET)
        draw_rect(arm_x, h - 10, 2, 2, p.SKIN)

        head_y = h - 24 + walk_bob
        draw_rect(5, head_y, 5, 6, p.SKIN)
        draw_pixel(5, head_y + 4, p.SKIN_SHADOW)

        # Eye
        draw_pixel(5, head_y + 2, (50, 50, 60))
        draw_pixel(5, head_y + 2, (255, 255, 255))

        # Hair (side)
        hair_y = head_y - 5 + walk_bob
        draw_rect(6 + hair_flow, hair_y, 6, 6, p.HAIR)
        draw_rect(4, hair_y + 1, 3, 5, p.HAIR)
        draw_rect(7, hair_y - 1, 3, 2, p.HAIR)
        draw_pixel(5, hair_y + 2, p.HAIR_HIGHLIGHT)

        # Earring
        draw_pixel(4, head_y + 3, p.EARRING)

    else:  # right
        # === RIGHT SIDE VIEW (mirror of left) ===

        boot_y = h - 4
        boot_x = 6 - (leg_phase - 1)
        draw_rect(boot_x, boot_y, 4, 4, p.BOOTS)
        draw_pixel(boot_x + 1, boot_y + 1, p.BOOTS_BUCKLE)

        leg_y = h - 10
        draw_rect(7, leg_y, 4, 6, p.PANTS)
        draw_pixel(10, leg_y + 1, p.PANTS_SHADOW)
        draw_pixel(8, leg_y + 3, p.PANTS_HIGHLIGHT)

        jacket_y = h - 18 + walk_bob
        draw_rect(6, jacket_y, 6, 8, p.JACKET)
        draw_rect(6, jacket_y + 1, 2, 4, p.JACKET_HIGHLIGHT)
        draw_pixel(10, jacket_y + 6, p.JACKET_ACCENT)

        # Arm
        arm_x = 10 + arm_swing
        draw_rect(arm_x, h - 15, 3, 5, p.JACKET)
        draw_rect(arm_x + 1, h - 10, 2, 2, p.SKIN)

        head_y = h - 24 + walk_bob
        draw_rect(6, head_y, 5, 6, p.SKIN)
        draw_pixel(10, head_y + 4, p.SKIN_SHADOW)

        # Eye
        draw_pixel(10, head_y + 2, (50, 50, 60))
        draw_pixel(10, head_y + 2, (255, 255, 255))

        # Hair (side)
        hair_y = head_y - 5 + walk_bob
        draw_rect(4 - hair_flow, hair_y, 6, 6, p.HAIR)
        draw_rect(9, hair_y + 1, 3, 5, p.HAIR)
        draw_rect(6, hair_y - 1, 3, 2, p.HAIR)
        draw_pixel(10, hair_y + 2, p.HAIR_HIGHLIGHT)

    return surface


def create_detailed_zombie_sprite(direction: str, frame: int, zombie_type: str = "scene",
                                   size: Tuple[int, int] = (16, 32)) -> pygame.Surface:
    """Create a detailed zombie sprite with shambling animation."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = ZombiePalette.get_palette(zombie_type)

    # Zombie-specific animation (more jerky, uneven)
    shamble_y = [0, -1, 1, 0][frame % 4]
    shamble_x = [0, 1, 0, -1][frame % 4]
    arm_hang = [1, 2, 2, 1][frame % 4]
    leg_drag = [0, 1, 2, 1][frame % 4]

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    if direction == "down":
        # Feet (one drags)
        draw_rect(4, h - 4 + leg_drag // 2, 3, 4, p["clothes_shadow"])
        draw_rect(9 - leg_drag // 2, h - 3, 3, 4, p["clothes_shadow"])

        # Legs (bent unevenly)
        draw_rect(4, h - 10, 3, 6, p["clothes"])
        draw_rect(9, h - 10, 3, 6, p["clothes"])

        # Hunched body
        body_y = h - 18 + shamble_y
        draw_rect(3, body_y, 10, 9, p["clothes"])
        draw_rect(4, body_y + 1, 8, 5, p["clothes_shadow"])

        # Arms (dangling, reaching)
        left_arm_y = h - 15 + arm_hang
        right_arm_y = h - 14 + arm_hang + 1
        draw_rect(1, left_arm_y, 2, 8, p["clothes"])
        draw_rect(13, right_arm_y, 2, 9, p["clothes"])
        # Grasping hands
        draw_rect(0, left_arm_y + 7, 3, 3, p["skin"])
        draw_rect(13, right_arm_y + 8, 3, 3, p["skin"])
        # Fingers
        draw_pixel(0, left_arm_y + 9, p["skin_shadow"])
        draw_pixel(14, right_arm_y + 10, p["skin_shadow"])

        # Head (tilted)
        head_y = h - 25 + shamble_y
        draw_rect(4 + shamble_x, head_y, 7, 7, p["skin"])
        # Sunken cheeks
        draw_rect(4 + shamble_x, head_y + 3, 2, 3, p["skin_shadow"])
        draw_rect(9 + shamble_x, head_y + 3, 2, 3, p["skin_shadow"])

        # Hollow eyes with glow
        draw_rect(5 + shamble_x, head_y + 2, 2, 2, (20, 20, 25))
        draw_rect(8 + shamble_x, head_y + 2, 2, 2, (20, 20, 25))
        draw_pixel(5 + shamble_x, head_y + 2, p["eyes"])
        draw_pixel(8 + shamble_x, head_y + 2, p["eyes"])

        # Mouth (open, groaning)
        draw_rect(6 + shamble_x, head_y + 5, 3, 2, (40, 30, 35))
        draw_pixel(7 + shamble_x, head_y + 5, (60, 40, 45))

        # Messy hair
        draw_rect(3, head_y - 2, 9, 4, p["hair"])
        draw_rect(2, head_y, 2, 3, p["hair"])
        draw_rect(11, head_y - 1, 2, 4, p["hair"])

        # Blood/wounds
        draw_pixel(6 + shamble_x, head_y + 4, p["blood"])
        draw_pixel(5, body_y + 3, p["blood"])

        # Special accessories by type
        if zombie_type == "bouncer" and "shades" in p:
            draw_rect(4 + shamble_x, head_y + 2, 8, 2, p["shades"])
        elif zombie_type == "dj" and "headphones" in p:
            draw_rect(3, head_y + 1, 2, 3, p["headphones"])
            draw_rect(10, head_y + 1, 2, 3, p["headphones"])
            draw_rect(4, head_y - 1, 7, 1, p["headphones"])

    elif direction == "up":
        draw_rect(4, h - 4, 3, 4, p["clothes_shadow"])
        draw_rect(9, h - 4, 3, 4, p["clothes_shadow"])
        draw_rect(4, h - 10, 3, 6, p["clothes"])
        draw_rect(9, h - 10, 3, 6, p["clothes"])

        body_y = h - 18 + shamble_y
        draw_rect(3, body_y, 10, 9, p["clothes"])

        draw_rect(1, h - 14 + arm_hang, 2, 9, p["clothes"])
        draw_rect(13, h - 15 + arm_hang, 2, 8, p["clothes"])

        head_y = h - 25 + shamble_y
        draw_rect(4, head_y, 7, 7, p["skin"])

        # Hair from back
        draw_rect(2, head_y - 2, 11, 6, p["hair"])

    elif direction == "left":
        draw_rect(5 + leg_drag // 2, h - 4, 4, 4, p["clothes_shadow"])
        draw_rect(5, h - 10, 4, 6, p["clothes"])

        body_y = h - 18 + shamble_y
        draw_rect(4, body_y, 7, 9, p["clothes"])

        # Extended arm
        draw_rect(1 - arm_hang, h - 13, 4, 9, p["clothes"])
        draw_rect(0 - arm_hang, h - 5, 3, 3, p["skin"])

        head_y = h - 25 + shamble_y
        draw_rect(5 + shamble_x, head_y, 6, 7, p["skin"])
        draw_rect(5 + shamble_x, head_y + 3, 1, 3, p["skin_shadow"])

        draw_rect(5 + shamble_x, head_y + 2, 2, 2, (20, 20, 25))
        draw_pixel(5 + shamble_x, head_y + 2, p["eyes"])

        draw_rect(5, head_y - 2, 7, 5, p["hair"])

    else:  # right
        draw_rect(7 - leg_drag // 2, h - 4, 4, 4, p["clothes_shadow"])
        draw_rect(7, h - 10, 4, 6, p["clothes"])

        body_y = h - 18 + shamble_y
        draw_rect(5, body_y, 7, 9, p["clothes"])

        # Extended arm
        draw_rect(11 + arm_hang, h - 13, 4, 9, p["clothes"])
        draw_rect(13 + arm_hang, h - 5, 3, 3, p["skin"])

        head_y = h - 25 + shamble_y
        draw_rect(5 - shamble_x, head_y, 6, 7, p["skin"])
        draw_rect(10 - shamble_x, head_y + 3, 1, 3, p["skin_shadow"])

        draw_rect(9 - shamble_x, head_y + 2, 2, 2, (20, 20, 25))
        draw_pixel(10 - shamble_x, head_y + 2, p["eyes"])

        draw_rect(4, head_y - 2, 7, 5, p["hair"])

    return surface


def create_hero_animations(scale: float = 2.5) -> Dict[str, List[pygame.Surface]]:
    """Generate complete hero animation set with scaling."""
    base_size = (16, 32)
    scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))

    animations: Dict[str, List[pygame.Surface]] = {}
    for direction in ["down", "up", "left", "right"]:
        frames = []
        for frame in range(4):
            sprite = create_detailed_hero_sprite(direction, frame, base_size)
            # Use smooth scaling for better quality at larger sizes
            scaled = pygame.transform.scale(sprite, scaled_size)
            frames.append(scaled)
        animations[direction] = frames
    return animations


def create_zombie_animations(zombie_type: str = "scene", scale: float = 2.5) -> Dict[str, List[pygame.Surface]]:
    """Generate complete zombie animation set."""
    base_size = (16, 32)
    scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))

    animations: Dict[str, List[pygame.Surface]] = {}
    for direction in ["down", "up", "left", "right"]:
        frames = []
        for frame in range(4):
            sprite = create_detailed_zombie_sprite(direction, frame, zombie_type, base_size)
            scaled = pygame.transform.scale(sprite, scaled_size)
            frames.append(scaled)
        animations[direction] = frames
    return animations


def create_detailed_item_icon(item_name: str, base_color: Color, size: Tuple[int, int] = (32, 32)) -> pygame.Surface:
    """Create a beautifully detailed item icon."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    item_lower = item_name.lower()

    if "flyer" in item_lower:
        # Neon gig flyer with concert details
        # Paper base
        draw_rect(4, 3, 24, 26, (250, 240, 220))
        draw_rect(5, 4, 22, 24, (255, 250, 235))

        # "TONIGHT" header in neon pink
        for i, x in enumerate([7, 9, 11, 13, 15, 17, 19]):
            draw_pixel(x, 6, (255, 50, 150))
            draw_pixel(x, 7, (255, 100, 180))

        # Band name area
        draw_rect(6, 10, 20, 8, (40, 20, 60))
        draw_rect(7, 11, 18, 6, (60, 30, 90))

        # "THE NEON DEAD" text suggestion
        for x in range(8, 24, 2):
            draw_pixel(x, 13, (255, 200, 50))
            draw_pixel(x, 14, (255, 180, 30))

        # Venue info
        draw_rect(8, 20, 16, 1, (100, 80, 60))
        draw_rect(10, 22, 12, 1, (100, 80, 60))
        draw_rect(9, 24, 14, 1, (100, 80, 60))

        # Folded corner
        draw_rect(24, 3, 4, 4, (220, 210, 190))
        draw_pixel(25, 4, (200, 190, 170))

        # Glow effect border
        for y in range(3, 29):
            draw_pixel(3, y, (255, 200, 100, 60))
            draw_pixel(28, y, (255, 200, 100, 60))

    elif "tape" in item_lower or "demo" in item_lower:
        # Cassette tape with detail
        # Outer shell
        draw_rect(3, 6, 26, 20, (50, 50, 65))
        draw_rect(4, 7, 24, 18, (40, 40, 55))

        # Label area
        draw_rect(6, 8, 20, 8, (140, 120, 180))
        draw_rect(7, 9, 18, 6, (160, 140, 200))

        # Handwritten text on label
        for x in range(8, 23, 2):
            draw_pixel(x, 11, (60, 40, 80))
        for x in range(10, 21, 2):
            draw_pixel(x, 13, (60, 40, 80))

        # Tape reels
        reel_y = 19
        # Left reel
        draw_rect(9, reel_y - 2, 6, 6, (30, 30, 40))
        draw_rect(10, reel_y - 1, 4, 4, (70, 60, 90))
        draw_rect(11, reel_y, 2, 2, (40, 40, 50))
        # Right reel
        draw_rect(17, reel_y - 2, 6, 6, (30, 30, 40))
        draw_rect(18, reel_y - 1, 4, 4, (70, 60, 90))
        draw_rect(19, reel_y, 2, 2, (40, 40, 50))

        # Tape visible between reels
        draw_rect(13, reel_y, 6, 1, (60, 40, 30))

        # Screw holes
        draw_pixel(5, 9, (30, 30, 35))
        draw_pixel(26, 9, (30, 30, 35))
        draw_pixel(5, 23, (30, 30, 35))
        draw_pixel(26, 23, (30, 30, 35))

    elif "pass" in item_lower or "backstage" in item_lower:
        # Laminated backstage pass
        # Pass body
        draw_rect(4, 2, 24, 28, (200, 60, 180))
        draw_rect(5, 3, 22, 26, (220, 80, 200))

        # Laminate shine
        draw_rect(5, 3, 20, 2, (255, 180, 240))
        draw_rect(5, 3, 2, 20, (255, 160, 230))

        # "BACKSTAGE" text area
        draw_rect(6, 6, 20, 6, (40, 20, 50))
        for x in range(8, 24, 2):
            draw_pixel(x, 8, (255, 255, 200))
            draw_pixel(x, 9, (255, 220, 150))

        # Star logo
        cx, cy = 16, 18
        star_color = (255, 230, 100)
        # Simple 5-point star
        for angle in range(0, 360, 72):
            rad = math.radians(angle - 90)
            x1 = cx + int(5 * math.cos(rad))
            y1 = cy + int(5 * math.sin(rad))
            draw_pixel(x1, y1, star_color)
            draw_pixel(x1 + 1, y1, star_color)
            draw_pixel(x1, y1 + 1, star_color)
        draw_rect(cx - 1, cy - 1, 3, 3, star_color)

        # Lanyard hole
        draw_rect(14, 2, 4, 3, (60, 40, 70))
        draw_rect(15, 2, 2, 2, (30, 20, 35))

        # "ALL ACCESS" at bottom
        draw_rect(8, 25, 16, 3, (255, 255, 255))
        for x in range(9, 23, 2):
            draw_pixel(x, 26, (180, 50, 160))

    elif "setlist" in item_lower:
        # Crumpled paper with handwritten setlist
        # Wrinkled paper
        paper = (245, 240, 230)
        paper_shadow = (220, 215, 200)
        paper_highlight = (255, 252, 245)

        draw_rect(3, 3, 26, 26, paper)

        # Wrinkle lines
        draw_rect(5, 8, 8, 1, paper_shadow)
        draw_rect(15, 5, 10, 1, paper_shadow)
        draw_rect(8, 18, 12, 1, paper_shadow)
        draw_rect(6, 24, 6, 1, paper_shadow)

        # Highlights
        draw_rect(4, 4, 3, 3, paper_highlight)
        draw_rect(22, 20, 4, 4, paper_highlight)

        # Handwritten lines (setlist entries)
        ink = (30, 30, 60)
        for i, y in enumerate([7, 11, 15, 19, 23]):
            line_len = 16 - (i % 3) * 3
            for x in range(6, 6 + line_len):
                if random.random() > 0.2:  # Slightly uneven handwriting
                    draw_pixel(x, y, ink)

        # Numbers
        for i, y in enumerate([7, 11, 15, 19, 23]):
            draw_pixel(4, y, ink)

        # Coffee ring stain
        stain = (180, 150, 120)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x = 23 + int(4 * math.cos(rad))
            y = 8 + int(4 * math.sin(rad))
            if 0 <= x < w and 0 <= y < h:
                draw_pixel(x, y, stain)

        # Folded corner
        draw_rect(3, 3, 5, 5, paper_shadow)
        draw_rect(3, 3, 3, 3, paper)

    else:
        # Generic item with nice styling
        draw_rect(4, 4, 24, 24, base_color)
        highlight = add_highlight(base_color, 50)
        shadow = shade_color(base_color, 0.7)
        draw_rect(4, 4, 24, 4, highlight)
        draw_rect(4, 4, 4, 24, highlight)
        draw_rect(4, 24, 24, 4, shadow)
        draw_rect(24, 4, 4, 24, shadow)
        draw_rect(6, 6, 20, 20, shade_color(base_color, 0.9))

    return surface


def create_heart_icon(full: bool = True, size: Tuple[int, int] = (14, 14)) -> pygame.Surface:
    """Create a detailed heart icon for health display."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    if full:
        main = (255, 50, 80)
        highlight = (255, 150, 170)
        shadow = (180, 30, 60)
        outline = (120, 20, 40)
    else:
        main = (60, 30, 40)
        highlight = (80, 50, 60)
        shadow = (40, 20, 30)
        outline = (30, 15, 25)

    # Heart shape
    # Top left bump
    pygame.draw.circle(surface, main, (4, 5), 4)
    # Top right bump
    pygame.draw.circle(surface, main, (10, 5), 4)
    # Bottom triangle
    pygame.draw.polygon(surface, main, [(0, 6), (14, 6), (7, 13)])

    # Highlights
    pygame.draw.circle(surface, highlight, (3, 4), 2)

    # Outline
    pygame.draw.circle(surface, outline, (4, 5), 4, 1)
    pygame.draw.circle(surface, outline, (10, 5), 4, 1)

    return surface


def create_verb_icon(verb: str, size: Tuple[int, int] = (28, 28)) -> pygame.Surface:
    """Create a stylized icon for verb buttons."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    colors = {
        "walk": ((70, 160, 220), (100, 190, 250)),
        "look": ((220, 200, 70), (250, 230, 100)),
        "use": ((120, 200, 120), (150, 230, 150)),
        "talk": ((220, 120, 160), (250, 150, 190)),
    }

    main_color, highlight = colors.get(verb.lower(), ((150, 150, 150), (180, 180, 180)))

    # Background
    pygame.draw.rect(surface, main_color, (2, 2, w - 4, h - 4), border_radius=4)
    pygame.draw.rect(surface, highlight, (3, 3, w - 6, 4), border_radius=2)

    # Icon symbols
    cx, cy = w // 2, h // 2

    if verb.lower() == "walk":
        # Footsteps
        pygame.draw.ellipse(surface, (255, 255, 255), (6, 8, 6, 10))
        pygame.draw.ellipse(surface, (255, 255, 255), (14, 12, 6, 10))
    elif verb.lower() == "look":
        # Eye
        pygame.draw.ellipse(surface, (255, 255, 255), (6, 10, 16, 10))
        pygame.draw.circle(surface, (60, 60, 80), (cx, cy + 1), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 1, cy), 1)
    elif verb.lower() == "use":
        # Hand/grab
        pygame.draw.rect(surface, (255, 255, 255), (10, 8, 8, 12))
        pygame.draw.rect(surface, (255, 255, 255), (6, 10, 4, 8))
        pygame.draw.rect(surface, (255, 255, 255), (18, 12, 4, 6))
    elif verb.lower() == "talk":
        # Speech bubble
        pygame.draw.ellipse(surface, (255, 255, 255), (6, 6, 16, 12))
        pygame.draw.polygon(surface, (255, 255, 255), [(8, 16), (12, 16), (6, 22)])

    # Border
    pygame.draw.rect(surface, (40, 40, 50), (2, 2, w - 4, h - 4), 2, border_radius=4)

    return surface


# ============================================================================
# NEW CORE CHARACTER SPRITES (24x48 pixels)
# ============================================================================


class MayaPalette:
    """Color palette for Maya - The Lost Bandmate (half-transformed)."""
    # Human side
    SKIN_HUMAN = (245, 210, 185)
    SKIN_HUMAN_SHADOW = (210, 175, 150)

    # Zombie side
    SKIN_ZOMBIE = (140, 180, 140)
    SKIN_ZOMBIE_SHADOW = (100, 140, 100)

    # Infected veins
    VEIN_COLOR = (120, 255, 120)
    VEIN_GLOW = (180, 255, 180)

    # Eyes
    EYE_HUMAN = (80, 60, 50)
    EYE_ZOMBIE_GLOW = (180, 255, 160)

    # Hair - wild rocker hair
    HAIR = (40, 10, 60)
    HAIR_HIGHLIGHT = (80, 30, 100)

    # Torn band t-shirt
    SHIRT = (140, 30, 160)
    SHIRT_SHADOW = (100, 20, 120)
    SHIRT_TEAR = (80, 15, 90)

    # Leather pants
    PANTS = (30, 25, 35)
    PANTS_HIGHLIGHT = (50, 45, 55)

    # Bass guitar
    BASS_BODY = (150, 80, 40)
    BASS_NECK = (90, 50, 25)
    BASS_STRINGS = (200, 200, 210)


def create_maya_sprite(frame: int = 0) -> pygame.Surface:
    """Create Maya - The Lost Bandmate sprite (24x48 pixels).

    Half-transformed zombie bassist with visible transformation.

    Frames:
    0 - Idle (breathing)
    1 - Walking
    2 - Playing bass
    3 - Transforming (veins glowing)
    """
    size = (24, 48)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = MayaPalette

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    # Animation variables
    bob = [0, -1, 0, -1][frame % 4]
    breathe = [0, 1, 0, -1][frame % 4]
    vein_pulse = [0, 1, 2, 1][frame % 4]

    # BOOTS
    draw_rect(6, h - 4, 4, 4, (20, 20, 25))
    draw_rect(14, h - 4, 4, 4, (20, 20, 25))

    # LEATHER PANTS
    draw_rect(6, h - 14, 4, 10, p.PANTS)
    draw_rect(14, h - 14, 4, 10, p.PANTS)
    draw_pixel(7, h - 12, p.PANTS_HIGHLIGHT)
    draw_pixel(15, h - 12, p.PANTS_HIGHLIGHT)

    # BASS GUITAR (strapped across back)
    if frame == 2:  # Playing bass
        # Bass in playing position
        draw_rect(4, h - 22, 3, 12, p.BASS_NECK)
        draw_rect(3, h - 16, 5, 8, p.BASS_BODY)
        draw_pixel(4, h - 14, p.BASS_STRINGS)
        draw_pixel(5, h - 13, p.BASS_STRINGS)
    else:
        # Bass on back
        draw_rect(16, h - 26, 2, 10, p.BASS_NECK)
        draw_rect(15, h - 20, 4, 6, p.BASS_BODY)

    # TORSO - torn band t-shirt
    torso_y = h - 26 + bob
    draw_rect(7, torso_y, 10, 12, p.SHIRT)
    # Tears in shirt
    draw_pixel(9, torso_y + 3, p.SHIRT_TEAR)
    draw_pixel(10, torso_y + 5, p.SHIRT_TEAR)
    draw_pixel(14, torso_y + 4, p.SHIRT_TEAR)
    # Shadow
    draw_rect(8, torso_y + 8, 8, 3, p.SHIRT_SHADOW)

    # ARMS
    arm_y = torso_y + 2
    # Left arm (zombie side - infected)
    draw_rect(4, arm_y, 3, 10, p.SKIN_ZOMBIE)
    draw_rect(4, arm_y + 8, 3, 3, p.SKIN_ZOMBIE_SHADOW)
    # Infected veins on zombie arm
    if vein_pulse > 0:
        draw_pixel(5, arm_y + 2, p.VEIN_GLOW if vein_pulse == 2 else p.VEIN_COLOR)
        draw_pixel(5, arm_y + 4, p.VEIN_GLOW if vein_pulse == 2 else p.VEIN_COLOR)
        draw_pixel(4, arm_y + 6, p.VEIN_COLOR)

    # Right arm (human side)
    draw_rect(17, arm_y, 3, 10, p.SKIN_HUMAN)
    draw_rect(17, arm_y + 8, 3, 3, p.SKIN_HUMAN_SHADOW)

    # HEAD
    head_y = h - 34 + bob + breathe
    # Split down the middle - human left, zombie right
    # Left side (human)
    draw_rect(8, head_y, 4, 8, p.SKIN_HUMAN)
    draw_pixel(8, head_y + 6, p.SKIN_HUMAN_SHADOW)

    # Right side (zombie)
    draw_rect(12, head_y, 4, 8, p.SKIN_ZOMBIE)
    draw_pixel(15, head_y + 6, p.SKIN_ZOMBIE_SHADOW)

    # EYES
    # Human eye (left)
    draw_pixel(9, head_y + 3, p.EYE_HUMAN)
    draw_pixel(9, head_y + 2, (255, 255, 255))  # Highlight

    # Zombie eye (right) - glowing
    draw_rect(13, head_y + 3, 2, 2, (20, 25, 20))
    draw_pixel(13, head_y + 3, p.EYE_ZOMBIE_GLOW)
    if vein_pulse == 2:  # Extra glow when transforming
        draw_pixel(12, head_y + 3, p.VEIN_GLOW)
        draw_pixel(15, head_y + 3, p.VEIN_GLOW)

    # MOUTH
    draw_rect(10, head_y + 6, 4, 1, (100, 60, 70))

    # WILD ROCKER HAIR
    hair_y = head_y - 6
    # Big volume on top
    draw_rect(6, hair_y, 12, 8, p.HAIR)
    # Side spikes
    draw_rect(5, hair_y + 2, 2, 6, p.HAIR)
    draw_rect(17, hair_y + 2, 2, 6, p.HAIR)
    # Top spikes
    draw_rect(8, hair_y - 2, 3, 3, p.HAIR)
    draw_rect(13, hair_y - 1, 3, 2, p.HAIR)
    # Highlights
    draw_pixel(9, hair_y + 1, p.HAIR_HIGHLIGHT)
    draw_pixel(14, hair_y + 2, p.HAIR_HIGHLIGHT)

    # TRANSFORMATION EFFECT (frame 3)
    if frame == 3:
        # Glowing veins across body
        for i in range(0, 8, 2):
            draw_pixel(10 + i % 4, torso_y + i, p.VEIN_GLOW)
            draw_pixel(11 + i % 3, torso_y + i + 1, p.VEIN_COLOR)

    return surface


class JohnnyChrommePalette:
    """Color palette for Johnny Chrome - The Friendly Zombie."""
    # Vintage 1950s suit
    SUIT = (140, 150, 160)
    SUIT_SHADOW = (100, 110, 120)
    SUIT_HIGHLIGHT = (180, 190, 200)

    # Shirt and tie
    SHIRT = (220, 220, 230)
    TIE = (60, 70, 80)

    # Zombie skin (but well-maintained)
    SKIN = (130, 160, 135)
    SKIN_SHADOW = (100, 130, 105)

    # Slicked hair (patchy)
    HAIR = (50, 55, 60)
    HAIR_SHINE = (100, 105, 110)

    # Sunglasses
    SHADES = (20, 20, 25)
    SHADES_GLINT = (180, 180, 200)

    # Shoes
    SHOES = (30, 30, 35)
    SHOES_SHINE = (80, 80, 90)

    # Cigarette
    CIGARETTE = (240, 240, 245)
    CIGARETTE_TIP = (200, 100, 50)


def create_johnny_chrome_sprite(frame: int = 0) -> pygame.Surface:
    """Create Johnny Chrome - The Friendly Zombie sprite (24x48 pixels).

    Lucid zombie in vintage 1950s suit with dignity despite decomposition.

    Frames:
    0 - Standing (dignified)
    1 - Gesturing
    2 - Contemplating
    3 - Grooving
    """
    size = (24, 48)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = JohnnyChrommePalette

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    # Animation variables
    sway = [0, -1, 0, 1][frame % 4] if frame == 3 else 0
    gesture_arm = [0, -3, -5, -3][frame % 4] if frame == 1 else 0

    # POLISHED SHOES
    draw_rect(7, h - 4, 4, 4, p.SHOES)
    draw_rect(13, h - 4, 4, 4, p.SHOES)
    draw_pixel(8, h - 3, p.SHOES_SHINE)
    draw_pixel(14, h - 3, p.SHOES_SHINE)

    # PANTS (vintage suit)
    draw_rect(7, h - 14, 4, 10, p.SUIT)
    draw_rect(13, h - 14, 4, 10, p.SUIT)
    # Crease
    draw_pixel(9, h - 12, p.SUIT_HIGHLIGHT)
    draw_pixel(15, h - 12, p.SUIT_HIGHLIGHT)
    draw_pixel(7, h - 10, p.SUIT_SHADOW)
    draw_pixel(13, h - 10, p.SUIT_SHADOW)

    # SUIT JACKET
    jacket_y = h - 26 + sway
    draw_rect(6, jacket_y, 12, 12, p.SUIT)
    # Lapels
    draw_rect(7, jacket_y, 2, 6, p.SUIT_SHADOW)
    draw_rect(15, jacket_y, 2, 6, p.SUIT_SHADOW)
    # Shirt and tie visible
    draw_rect(9, jacket_y + 1, 6, 8, p.SHIRT)
    draw_rect(11, jacket_y + 1, 2, 8, p.TIE)
    # Jacket highlights
    draw_pixel(6, jacket_y + 1, p.SUIT_HIGHLIGHT)
    draw_pixel(17, jacket_y + 1, p.SUIT_HIGHLIGHT)

    # ARMS
    arm_y = jacket_y + 3
    # Left arm (gesturing in frame 1)
    left_arm_y = arm_y + gesture_arm
    draw_rect(3, left_arm_y, 3, 8, p.SUIT)
    draw_rect(3, left_arm_y + 6, 3, 3, p.SKIN)

    # Right arm
    draw_rect(18, arm_y, 3, 8, p.SUIT)
    draw_rect(18, arm_y + 6, 3, 3, p.SKIN)

    # HEAD
    head_y = h - 36 + sway
    draw_rect(8, head_y, 8, 9, p.SKIN)
    # Sunken cheeks (zombie trait)
    draw_pixel(8, head_y + 5, p.SKIN_SHADOW)
    draw_pixel(15, head_y + 5, p.SKIN_SHADOW)

    # SUNGLASSES (hiding hollow eyes)
    draw_rect(8, head_y + 3, 8, 3, p.SHADES)
    draw_pixel(9, head_y + 3, p.SHADES_GLINT)
    draw_pixel(14, head_y + 3, p.SHADES_GLINT)

    # MOUTH (dignified, closed)
    draw_rect(10, head_y + 7, 4, 1, (80, 90, 85))

    # CIGARETTE (unlit - he's undead, doesn't need to inhale)
    draw_rect(7, head_y + 7, 3, 1, p.CIGARETTE)
    draw_pixel(6, head_y + 7, p.CIGARETTE_TIP)

    # SLICKED BACK HAIR (now patchy)
    hair_y = head_y - 4
    draw_rect(7, hair_y, 10, 6, p.HAIR)
    # Patches missing
    draw_pixel(9, hair_y + 2, p.SKIN)
    draw_pixel(13, hair_y + 3, p.SKIN)
    # Shine (still tries to maintain it)
    draw_pixel(10, hair_y + 1, p.HAIR_SHINE)
    draw_pixel(14, hair_y + 1, p.HAIR_SHINE)

    # CONTEMPLATING GESTURE (frame 2)
    if frame == 2:
        # Hand to chin
        draw_rect(16, head_y + 6, 3, 2, p.SKIN)

    return surface


class PromoterPalette:
    """Color palette for The Promoter - The Villain."""
    # Power suit (80s excess)
    SUIT = (140, 20, 30)
    SUIT_SHADOW = (100, 10, 20)
    SUIT_HIGHLIGHT = (180, 40, 50)

    # Shoulder pads (MASSIVE)
    SHOULDER_PAD = (160, 30, 40)

    # Shirt
    SHIRT = (240, 230, 235)

    # Tie with occult symbols
    TIE = (20, 20, 25)
    OCCULT_SYMBOL = (200, 50, 60)

    # Skin (sinister)
    SKIN = (240, 220, 200)
    SKIN_SHADOW = (200, 180, 160)

    # Slicked hair
    HAIR = (30, 25, 30)
    HAIR_PRODUCT = (60, 55, 60)

    # Gold chains
    GOLD = (255, 215, 0)
    GOLD_SHADOW = (200, 170, 0)

    # Pants
    PANTS = (25, 20, 30)
    PANTS_HIGHLIGHT = (45, 40, 50)

    # Shoes (expensive)
    SHOES = (20, 15, 25)
    SHOES_SHINE = (100, 90, 110)

    # Contracts
    PAPER = (250, 245, 240)
    INK = (30, 30, 40)


def create_promoter_sprite(frame: int = 0) -> pygame.Surface:
    """Create The Promoter - The Villain sprite (24x48 pixels).

    Sleazy 80s music industry executive with hidden occult power.

    Frames:
    0 - Intimidating stance
    1 - Scheming
    2 - Ritual casting
    3 - Transforming (revealing true nature)
    """
    size = (24, 48)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = PromoterPalette

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    # Animation variables
    ritual_glow = [0, 1, 2, 3][frame % 4] if frame == 2 else 0
    transform_intensity = [0, 0, 0, 3][frame % 4]

    # EXPENSIVE SHOES
    draw_rect(7, h - 4, 4, 4, p.SHOES)
    draw_rect(13, h - 4, 4, 4, p.SHOES)
    draw_pixel(8, h - 3, p.SHOES_SHINE)
    draw_pixel(14, h - 3, p.SHOES_SHINE)

    # PANTS (black, expensive)
    draw_rect(7, h - 14, 4, 10, p.PANTS)
    draw_rect(13, h - 14, 4, 10, p.PANTS)
    draw_pixel(9, h - 11, p.PANTS_HIGHLIGHT)
    draw_pixel(15, h - 11, p.PANTS_HIGHLIGHT)

    # POWER SUIT JACKET
    jacket_y = h - 28
    draw_rect(5, jacket_y, 14, 14, p.SUIT)

    # MASSIVE 80s SHOULDER PADS
    draw_rect(3, jacket_y, 4, 5, p.SHOULDER_PAD)
    draw_rect(17, jacket_y, 4, 5, p.SHOULDER_PAD)
    draw_pixel(3, jacket_y, p.SUIT_HIGHLIGHT)
    draw_pixel(20, jacket_y, p.SUIT_HIGHLIGHT)

    # Shirt and tie visible
    draw_rect(9, jacket_y + 2, 6, 10, p.SHIRT)
    draw_rect(11, jacket_y + 2, 2, 10, p.TIE)

    # OCCULT SYMBOLS on tie
    draw_pixel(11, jacket_y + 5, p.OCCULT_SYMBOL)
    draw_pixel(12, jacket_y + 7, p.OCCULT_SYMBOL)
    if ritual_glow > 1:
        # Symbols glow during ritual
        draw_pixel(11, jacket_y + 5, (255, 100, 120))
        draw_pixel(12, jacket_y + 7, (255, 100, 120))

    # GOLD CHAINS (multiple)
    draw_rect(9, jacket_y + 1, 6, 1, p.GOLD)
    draw_pixel(10, jacket_y + 2, p.GOLD)
    draw_pixel(13, jacket_y + 2, p.GOLD_SHADOW)

    # ARMS
    arm_y = jacket_y + 4
    draw_rect(2, arm_y, 3, 10, p.SUIT)
    draw_rect(19, arm_y, 3, 10, p.SUIT)

    # HANDS
    # Left hand holding contracts (frame 0, 1)
    if frame < 2:
        draw_rect(2, arm_y + 8, 3, 4, p.SKIN)
        # Contracts
        draw_rect(0, arm_y + 6, 4, 6, p.PAPER)
        draw_pixel(1, arm_y + 7, p.INK)
        draw_pixel(2, arm_y + 8, p.INK)
    elif frame == 2:
        # Hands raised for ritual
        draw_rect(1, arm_y - 4, 3, 4, p.SKIN)
        draw_rect(20, arm_y - 4, 3, 4, p.SKIN)
        # Ritual energy
        draw_pixel(2, arm_y - 5, (255, 50, 80))
        draw_pixel(21, arm_y - 5, (255, 50, 80))
    else:
        draw_rect(2, arm_y + 8, 3, 4, p.SKIN)

    # Right hand
    draw_rect(19, arm_y + 8, 3, 4, p.SKIN)

    # HEAD
    head_y = h - 38
    draw_rect(8, head_y, 8, 10, p.SKIN)
    draw_pixel(8, head_y + 7, p.SKIN_SHADOW)
    draw_pixel(15, head_y + 7, p.SKIN_SHADOW)

    # SINISTER SMILE
    draw_rect(9, head_y + 7, 6, 2, (120, 80, 90))
    draw_pixel(10, head_y + 8, (255, 255, 255))  # Tooth glint

    # EYES (scheming)
    if frame == 1:
        # Narrowed eyes (scheming)
        draw_rect(9, head_y + 4, 2, 1, (40, 30, 35))
        draw_rect(13, head_y + 4, 2, 1, (40, 30, 35))
    elif transform_intensity > 0:
        # Eyes glow red when transforming
        draw_rect(9, head_y + 4, 2, 2, (255, 50, 50))
        draw_rect(13, head_y + 4, 2, 2, (255, 50, 50))
    else:
        draw_pixel(9, head_y + 4, (40, 30, 35))
        draw_pixel(13, head_y + 4, (40, 30, 35))

    # SLICKED HAIR
    hair_y = head_y - 4
    draw_rect(7, hair_y, 10, 6, p.HAIR)
    # Product shine
    draw_rect(9, hair_y, 6, 2, p.HAIR_PRODUCT)

    # TRANSFORMATION EFFECT (frame 3)
    if transform_intensity > 0:
        # Dark aura
        for i in range(4):
            draw_pixel(6 - i, jacket_y + i * 3, (80, 20, 30))
            draw_pixel(17 + i, jacket_y + i * 3, (80, 20, 30))

    return surface


class ClerkPalette:
    """Color palette for Record Store Clerk."""
    # Flannel shirt (grunge aesthetic)
    FLANNEL_BASE = (140, 60, 50)
    FLANNEL_CHECK = (100, 40, 35)
    FLANNEL_LIGHT = (180, 90, 75)

    # Band tee underneath
    BAND_TEE = (30, 30, 35)
    BAND_LOGO = (200, 180, 100)

    # Jeans
    JEANS = (60, 70, 90)
    JEANS_SHADOW = (40, 50, 70)
    JEANS_HIGHLIGHT = (80, 90, 110)

    # Skin
    SKIN = (240, 210, 190)
    SKIN_SHADOW = (200, 170, 150)

    # Hair (messy)
    HAIR = (70, 50, 40)
    HAIR_SHADOW = (50, 35, 25)

    # Thick-rimmed glasses
    GLASSES_FRAME = (30, 30, 35)
    GLASSES_LENS = (180, 200, 220, 100)
    GLASSES_GLINT = (255, 255, 255)

    # Sneakers
    SNEAKERS = (200, 200, 210)
    SNEAKERS_SOLE = (240, 240, 250)

    # Vinyl record
    VINYL = (20, 20, 25)
    VINYL_LABEL = (180, 50, 80)

    # Coffee cup
    COFFEE_CUP = (240, 230, 220)
    COFFEE = (80, 60, 50)


def create_clerk_sprite(frame: int = 0) -> pygame.Surface:
    """Create Record Store Clerk sprite (24x48 pixels).

    Knowledgeable music nerd with impeccable taste.

    Frames:
    0 - Flipping through records
    1 - Nodding to music
    2 - Talking (recommending)
    3 - Pointing (showing you something)
    """
    size = (24, 48)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = ClerkPalette

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    # Animation variables
    nod = [0, -2, 0, 0][frame % 4] if frame == 1 else 0

    # SNEAKERS
    draw_rect(7, h - 4, 4, 4, p.SNEAKERS)
    draw_rect(13, h - 4, 4, 4, p.SNEAKERS)
    draw_rect(7, h - 2, 4, 2, p.SNEAKERS_SOLE)
    draw_rect(13, h - 2, 4, 2, p.SNEAKERS_SOLE)

    # JEANS
    draw_rect(7, h - 14, 4, 10, p.JEANS)
    draw_rect(13, h - 14, 4, 10, p.JEANS)
    draw_pixel(7, h - 12, p.JEANS_SHADOW)
    draw_pixel(9, h - 10, p.JEANS_HIGHLIGHT)
    draw_pixel(13, h - 12, p.JEANS_SHADOW)
    draw_pixel(15, h - 10, p.JEANS_HIGHLIGHT)

    # FLANNEL SHIRT (slightly hunched crate-digger posture)
    shirt_y = h - 26
    draw_rect(6, shirt_y, 12, 12, p.FLANNEL_BASE)
    # Plaid pattern
    for i in range(0, 12, 3):
        draw_rect(6, shirt_y + i, 12, 1, p.FLANNEL_CHECK)
    for i in range(0, 12, 4):
        draw_rect(6 + i, shirt_y, 1, 12, p.FLANNEL_CHECK)
    # Lighter stripes
    draw_rect(6, shirt_y + 5, 12, 1, p.FLANNEL_LIGHT)

    # Band tee visible at collar
    draw_rect(10, shirt_y, 4, 3, p.BAND_TEE)
    draw_pixel(11, shirt_y + 1, p.BAND_LOGO)
    draw_pixel(12, shirt_y + 1, p.BAND_LOGO)

    # ARMS
    arm_y = shirt_y + 3
    # Left arm - holding vinyl record (frame 0) or pointing (frame 3)
    if frame == 3:
        # Pointing
        draw_rect(2, arm_y - 2, 3, 8, p.FLANNEL_BASE)
        draw_rect(1, arm_y + 4, 4, 2, p.SKIN)
        draw_pixel(0, arm_y + 4, p.SKIN)  # Pointing finger
    else:
        draw_rect(3, arm_y, 3, 8, p.FLANNEL_BASE)
        draw_rect(3, arm_y + 6, 3, 4, p.SKIN)
        if frame == 0:
            # Vinyl record in hand
            draw_rect(1, arm_y + 4, 5, 5, p.VINYL)
            draw_rect(2, arm_y + 5, 3, 3, p.VINYL_LABEL)

    # Right arm
    draw_rect(18, arm_y, 3, 8, p.FLANNEL_BASE)
    draw_rect(18, arm_y + 6, 3, 4, p.SKIN)

    # COFFEE CUP (always nearby)
    draw_rect(20, shirt_y + 10, 3, 4, p.COFFEE_CUP)
    draw_rect(20, shirt_y + 11, 3, 3, p.COFFEE)

    # HEAD
    head_y = h - 36 + nod
    draw_rect(8, head_y, 8, 9, p.SKIN)
    draw_pixel(8, head_y + 6, p.SKIN_SHADOW)
    draw_pixel(15, head_y + 6, p.SKIN_SHADOW)

    # THICK-RIMMED GLASSES
    draw_rect(8, head_y + 3, 3, 4, p.GLASSES_FRAME)
    draw_rect(13, head_y + 3, 3, 4, p.GLASSES_FRAME)
    # Lenses (with transparency)
    draw_rect(9, head_y + 4, 2, 3, p.GLASSES_LENS)
    draw_rect(14, head_y + 4, 2, 3, p.GLASSES_LENS)
    # Glint
    draw_pixel(9, head_y + 4, p.GLASSES_GLINT)

    # Bridge of glasses
    draw_rect(11, head_y + 5, 2, 1, p.GLASSES_FRAME)

    # MOUTH (talking in frame 2)
    if frame == 2:
        draw_rect(10, head_y + 7, 4, 2, (120, 90, 80))
    else:
        draw_rect(11, head_y + 7, 2, 1, (120, 90, 80))

    # MESSY HAIR
    hair_y = head_y - 4
    draw_rect(7, hair_y, 10, 6, p.HAIR)
    # Messy tufts
    draw_rect(6, hair_y + 1, 2, 3, p.HAIR)
    draw_rect(16, hair_y + 2, 2, 3, p.HAIR)
    draw_rect(10, hair_y - 1, 3, 2, p.HAIR)
    # Shadow
    draw_pixel(8, hair_y + 4, p.HAIR_SHADOW)
    draw_pixel(14, hair_y + 3, p.HAIR_SHADOW)

    return surface


class DJRottenPalette:
    """Color palette for DJ Rotten."""
    # Leather jacket (punk rock)
    LEATHER = (30, 25, 35)
    LEATHER_SHADOW = (20, 15, 25)
    LEATHER_HIGHLIGHT = (50, 45, 55)

    # Band patches on jacket
    PATCH_1 = (200, 50, 80)
    PATCH_2 = (100, 200, 100)
    PATCH_3 = (220, 180, 50)

    # T-shirt underneath
    SHIRT = (50, 50, 60)

    # Tight pants
    PANTS = (40, 40, 50)
    PANTS_HIGHLIGHT = (60, 60, 70)

    # Skin (zombie but still rocking)
    SKIN = (140, 170, 145)
    SKIN_SHADOW = (100, 130, 105)

    # Punk mohawk
    MOHAWK = (180, 50, 90)
    MOHAWK_SHADOW = (140, 30, 70)
    MOHAWK_TIP = (220, 100, 140)

    # Headphones
    HEADPHONE_BAND = (40, 40, 50)
    HEADPHONE_CUP = (60, 60, 75)
    HEADPHONE_FOAM = (80, 80, 95)

    # Microphone
    MIC_HANDLE = (120, 130, 140)
    MIC_HEAD = (100, 110, 120)
    MIC_GRILLE = (140, 150, 160)

    # Boots (combat style)
    BOOTS = (25, 25, 30)
    BOOTS_LACES = (200, 200, 210)


def create_dj_rotten_sprite(frame: int = 0) -> pygame.Surface:
    """Create DJ Rotten sprite (24x48 pixels).

    Punk rock radio DJ zombie who won't let death stop the music.

    Frames:
    0 - Spinning records (hands on turntables)
    1 - Announcing (mic to mouth)
    2 - Headbanging
    3 - Pointing at listener
    """
    size = (24, 48)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    p = DJRottenPalette

    def draw_pixel(x: int, y: int, color: Color) -> None:
        if 0 <= x < w and 0 <= y < h:
            surface.set_at((x, y), color)

    def draw_rect(x: int, y: int, rw: int, rh: int, color: Color) -> None:
        for dy in range(rh):
            for dx in range(rw):
                draw_pixel(x + dx, y + dy, color)

    # Animation variables
    headbang = [0, -3, -1, 0][frame % 4] if frame == 2 else 0
    mohawk_sway = [-1, 0, 1, 0][frame % 4] if frame == 2 else 0

    # COMBAT BOOTS
    draw_rect(7, h - 5, 4, 5, p.BOOTS)
    draw_rect(13, h - 5, 4, 5, p.BOOTS)
    # Laces
    draw_pixel(8, h - 4, p.BOOTS_LACES)
    draw_pixel(9, h - 3, p.BOOTS_LACES)
    draw_pixel(14, h - 4, p.BOOTS_LACES)
    draw_pixel(15, h - 3, p.BOOTS_LACES)

    # TIGHT PANTS
    draw_rect(7, h - 15, 4, 10, p.PANTS)
    draw_rect(13, h - 15, 4, 10, p.PANTS)
    draw_pixel(9, h - 13, p.PANTS_HIGHLIGHT)
    draw_pixel(15, h - 13, p.PANTS_HIGHLIGHT)

    # LEATHER JACKET
    jacket_y = h - 28
    draw_rect(5, jacket_y, 14, 13, p.LEATHER)
    # Highlights
    draw_pixel(6, jacket_y + 1, p.LEATHER_HIGHLIGHT)
    draw_pixel(17, jacket_y + 1, p.LEATHER_HIGHLIGHT)
    # Shadow
    draw_rect(7, jacket_y + 9, 10, 3, p.LEATHER_SHADOW)

    # BAND PATCHES on jacket
    draw_rect(6, jacket_y + 3, 3, 3, p.PATCH_1)
    draw_rect(15, jacket_y + 5, 3, 3, p.PATCH_2)
    draw_pixel(10, jacket_y + 2, p.PATCH_3)
    draw_pixel(11, jacket_y + 2, p.PATCH_3)

    # T-shirt visible at collar
    draw_rect(10, jacket_y, 4, 3, p.SHIRT)

    # ARMS
    arm_y = jacket_y + 4
    # Left arm
    if frame == 0:
        # Hands on turntables
        draw_rect(2, arm_y + 2, 3, 8, p.LEATHER)
        draw_rect(2, arm_y + 8, 3, 3, p.SKIN)
    elif frame == 1:
        # Holding microphone
        draw_rect(3, arm_y - 2, 3, 10, p.LEATHER)
        draw_rect(3, arm_y + 6, 3, 4, p.SKIN)
        # Microphone
        draw_rect(4, arm_y - 4, 2, 4, p.MIC_HANDLE)
        draw_rect(3, arm_y - 6, 4, 3, p.MIC_HEAD)
        draw_pixel(4, arm_y - 5, p.MIC_GRILLE)
        draw_pixel(5, arm_y - 5, p.MIC_GRILLE)
    elif frame == 3:
        # Pointing
        draw_rect(2, arm_y - 1, 3, 8, p.LEATHER)
        draw_rect(1, arm_y + 5, 4, 3, p.SKIN)
        draw_pixel(0, arm_y + 5, p.SKIN)  # Pointing finger
    else:
        draw_rect(3, arm_y, 3, 9, p.LEATHER)
        draw_rect(3, arm_y + 7, 3, 3, p.SKIN)

    # Right arm
    draw_rect(18, arm_y, 3, 9, p.LEATHER)
    draw_rect(18, arm_y + 7, 3, 3, p.SKIN)

    # HEAD
    head_y = h - 38 + headbang
    draw_rect(8, head_y, 8, 9, p.SKIN)
    draw_pixel(8, head_y + 6, p.SKIN_SHADOW)
    draw_pixel(15, head_y + 6, p.SKIN_SHADOW)

    # EYES (intense)
    draw_pixel(9, head_y + 4, (40, 35, 40))
    draw_pixel(14, head_y + 4, (40, 35, 40))

    # MOUTH (shouting in frame 1)
    if frame == 1:
        draw_rect(10, head_y + 6, 4, 3, (80, 70, 75))
    else:
        draw_rect(10, head_y + 7, 4, 1, (80, 70, 75))

    # HEADPHONES (one cup on ear, one off)
    # Headband
    draw_rect(7, head_y - 2, 10, 2, p.HEADPHONE_BAND)
    # Left cup (on ear)
    draw_rect(6, head_y + 1, 3, 5, p.HEADPHONE_CUP)
    draw_rect(7, head_y + 2, 2, 4, p.HEADPHONE_FOAM)
    # Right cup (around neck area)
    draw_rect(17, head_y + 6, 3, 4, p.HEADPHONE_CUP)
    draw_rect(18, head_y + 7, 2, 3, p.HEADPHONE_FOAM)

    # PUNK MOHAWK (slightly wilted)
    mohawk_x = 10 + mohawk_sway
    # Base
    draw_rect(mohawk_x, head_y - 8, 4, 10, p.MOHAWK)
    # Spikes
    draw_rect(mohawk_x + 1, head_y - 10, 2, 3, p.MOHAWK)
    draw_rect(mohawk_x, head_y - 7, 4, 2, p.MOHAWK_SHADOW)
    # Tips (lighter)
    draw_pixel(mohawk_x + 1, head_y - 10, p.MOHAWK_TIP)
    draw_pixel(mohawk_x + 2, head_y - 9, p.MOHAWK_TIP)
    # Sides (shaved)
    draw_rect(7, head_y - 1, 2, 3, p.SKIN_SHADOW)
    draw_rect(15, head_y - 1, 2, 3, p.SKIN_SHADOW)

    return surface
