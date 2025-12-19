"""Stunning procedural background generation for each location.

Creates detailed, atmospheric pixel art backgrounds with:
- Multi-layer parallax depth
- Neon lighting effects
- Architectural details
- Atmospheric elements (fog, particles)
- Period-accurate 1982 Minneapolis aesthetics
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import pygame
import math
import random

Color = Tuple[int, int, int]


def create_gradient(surface: pygame.Surface, colors: List[Color], vertical: bool = True) -> None:
    """Create a smooth gradient on the surface."""
    width, height = surface.get_size()

    if len(colors) < 2:
        surface.fill(colors[0] if colors else (0, 0, 0))
        return

    steps = len(colors) - 1
    size = height if vertical else width

    for i in range(size):
        ratio = i / max(1, size - 1)
        segment = min(int(ratio * steps), steps - 1)
        local_ratio = ratio * steps - segment

        c1 = colors[segment]
        c2 = colors[segment + 1]

        color = (
            int(c1[0] + (c2[0] - c1[0]) * local_ratio),
            int(c1[1] + (c2[1] - c1[1]) * local_ratio),
            int(c1[2] + (c2[2] - c1[2]) * local_ratio),
        )

        if vertical:
            pygame.draw.line(surface, color, (0, i), (width, i))
        else:
            pygame.draw.line(surface, color, (i, 0), (i, height))


def draw_neon_sign(surface: pygame.Surface, text: str, pos: Tuple[int, int],
                   color: Color, font_size: int = 12, flicker: float = 1.0) -> None:
    """Draw a glowing neon sign."""
    try:
        font = pygame.font.Font(None, font_size)
    except:
        return

    # Glow layers (outer to inner)
    for i in range(4, 0, -1):
        alpha = int(40 * flicker)
        glow_color = (*color, alpha)
        glow_surf = font.render(text, True, color)
        glow_surf.set_alpha(alpha)
        for ox in range(-i, i + 1):
            for oy in range(-i, i + 1):
                surface.blit(glow_surf, (pos[0] + ox, pos[1] + oy))

    # Core text
    core = font.render(text, True, (255, 255, 255))
    surface.blit(core, pos)


def draw_building_silhouette(surface: pygame.Surface, x: int, width: int,
                             height: int, color: Color, windows: bool = True) -> None:
    """Draw a building silhouette with optional lit windows."""
    y = surface.get_height() - height
    pygame.draw.rect(surface, color, (x, y, width, height))

    # Roof detail
    roof_color = tuple(min(255, c + 15) for c in color)
    pygame.draw.rect(surface, roof_color, (x, y, width, 3))

    if windows:
        window_color = (255, 230, 150, 180)
        dark_window = (40, 35, 50)

        # Window grid
        win_w, win_h = 6, 8
        margin = 8
        cols = max(1, (width - margin * 2) // (win_w + 4))
        rows = max(1, (height - 20) // (win_h + 6))

        for row in range(rows):
            for col in range(cols):
                wx = x + margin + col * (win_w + 4)
                wy = y + 12 + row * (win_h + 6)

                # Random lit/dark windows
                if random.random() > 0.3:
                    pygame.draw.rect(surface, window_color[:3], (wx, wy, win_w, win_h))
                    # Curtain variation
                    if random.random() > 0.5:
                        pygame.draw.rect(surface, (200, 180, 120), (wx, wy, win_w, 3))
                else:
                    pygame.draw.rect(surface, dark_window, (wx, wy, win_w, win_h))


def draw_stars(surface: pygame.Surface, count: int = 30) -> None:
    """Draw twinkling stars in the sky."""
    width, height = surface.get_size()
    sky_height = height // 3

    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, sky_height)
        brightness = random.randint(150, 255)
        size = random.choice([1, 1, 1, 2])

        if size == 1:
            surface.set_at((x, y), (brightness, brightness, brightness))
        else:
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)

            # Twinkle rays for larger stars (use dimmer color since surface is not SRCALPHA)
            if random.random() > 0.7:
                ray_brightness = brightness // 2  # Simulate alpha by reducing brightness
                pygame.draw.line(surface, (ray_brightness, ray_brightness, ray_brightness),
                               (x - 2, y), (x + 2, y))
                pygame.draw.line(surface, (ray_brightness, ray_brightness, ray_brightness),
                               (x, y - 2), (x, y + 2))


def create_hennepin_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the Hennepin Avenue / First Avenue exterior background."""
    surface = pygame.Surface(size)
    w, h = size

    # Night sky gradient
    create_gradient(surface, [
        (10, 5, 30),
        (30, 15, 60),
        (50, 25, 80),
        (20, 10, 40),
    ])

    # Stars
    draw_stars(surface, 40)

    # Distant city skyline
    for i in range(5):
        bx = i * 70 - 20
        bw = random.randint(40, 60)
        bh = random.randint(40, 70)
        draw_building_silhouette(surface, bx, bw, bh, (25, 20, 45), windows=True)

    # Street level ground
    ground_y = h - 55
    pygame.draw.rect(surface, (25, 25, 40), (0, ground_y, w, 60))

    # Sidewalk
    pygame.draw.rect(surface, (50, 50, 65), (0, ground_y, w, 8))
    pygame.draw.rect(surface, (60, 60, 75), (0, ground_y, w, 2))

    # === FIRST AVENUE BUILDING ===
    # Main building structure
    building_x = 160
    building_w = 100
    building_h = 130
    building_y = h - building_h - 50

    pygame.draw.rect(surface, (35, 30, 50), (building_x, building_y, building_w, building_h))
    pygame.draw.rect(surface, (45, 40, 60), (building_x, building_y, building_w, 4))

    # Famous First Avenue star
    star_x, star_y = building_x + building_w // 2, building_y + 20
    star_color = (255, 255, 200)
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        x1 = star_x + int(12 * math.cos(angle))
        y1 = star_y + int(12 * math.sin(angle))
        angle2 = math.radians(i * 72 - 90 + 36)
        x2 = star_x + int(5 * math.cos(angle2))
        y2 = star_y + int(5 * math.sin(angle2))
        pygame.draw.line(surface, star_color, (star_x, star_y), (x1, y1), 2)
    pygame.draw.circle(surface, star_color, (star_x, star_y), 4)

    # Entrance door
    door_x = building_x + 35
    pygame.draw.rect(surface, (20, 20, 30), (door_x, h - 100, 30, 50))
    pygame.draw.rect(surface, (80, 70, 60), (door_x, h - 100, 30, 3))
    # Door handle
    pygame.draw.circle(surface, (180, 160, 100), (door_x + 25, h - 75), 2)

    # Marquee
    pygame.draw.rect(surface, (60, 50, 80), (building_x + 10, building_y + 40, 80, 25))
    pygame.draw.rect(surface, (200, 180, 100), (building_x + 10, building_y + 40, 80, 2))
    pygame.draw.rect(surface, (200, 180, 100), (building_x + 10, building_y + 63, 80, 2))

    # Marquee text
    draw_neon_sign(surface, "THE NEON DEAD", (building_x + 18, building_y + 46),
                   (255, 100, 200), font_size=14)

    # === LEFT BUILDING (Record Store) ===
    store_x = 40
    store_w = 80
    store_h = 90
    store_y = h - store_h - 50

    pygame.draw.rect(surface, (50, 45, 70), (store_x, store_y, store_w, store_h))

    # Store window
    pygame.draw.rect(surface, (30, 25, 45), (store_x + 10, store_y + 30, 60, 40))
    pygame.draw.rect(surface, (100, 80, 60), (store_x + 10, store_y + 30, 60, 2))

    # Neon "OPEN" sign
    draw_neon_sign(surface, "OPEN", (store_x + 25, store_y + 45), (100, 255, 150), 12)

    # Store name
    pygame.draw.rect(surface, (40, 35, 55), (store_x + 5, store_y + 8, 70, 16))
    draw_neon_sign(surface, "LET IT BE", (store_x + 12, store_y + 10), (255, 150, 50), 12)

    # === POSTER KIOSK ===
    kiosk_x = 15
    pygame.draw.rect(surface, (60, 55, 75), (kiosk_x, h - 110, 20, 60))
    pygame.draw.rect(surface, (70, 65, 85), (kiosk_x, h - 110, 20, 3))

    # Posters on kiosk
    poster_colors = [(255, 180, 60), (255, 100, 150), (100, 200, 255)]
    for i, color in enumerate(poster_colors):
        py = h - 105 + i * 18
        pygame.draw.rect(surface, color, (kiosk_x + 3, py, 14, 15))
        # Poster details
        pygame.draw.rect(surface, tuple(c - 40 for c in color), (kiosk_x + 5, py + 2, 10, 3))
        pygame.draw.rect(surface, tuple(c - 40 for c in color), (kiosk_x + 5, py + 7, 10, 2))

    # === ALLEY ENTRANCE (to radio station) ===
    alley_x = w - 50
    pygame.draw.rect(surface, (15, 12, 25), (alley_x, h - 120, 35, 70))
    # Graffiti arrow
    pygame.draw.polygon(surface, (150, 100, 200),
                       [(alley_x + 5, h - 90), (alley_x + 20, h - 100), (alley_x + 20, h - 80)])

    # === STREET DETAILS ===
    # Street lights
    for lx in [80, 200, 290]:
        pygame.draw.rect(surface, (60, 60, 70), (lx, h - 140, 4, 90))
        # Light glow
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.circle(surface, (255, 240, 200),
                             (lx + 2, h - 145), 8 + i * 4)

    # Puddle reflections
    pygame.draw.ellipse(surface, (40, 35, 60), (100, h - 40, 40, 8))
    pygame.draw.ellipse(surface, (60, 50, 90), (102, h - 39, 36, 5))

    # Manhole cover
    pygame.draw.circle(surface, (50, 50, 60), (250, h - 35), 8)
    pygame.draw.circle(surface, (40, 40, 50), (250, h - 35), 6)

    return surface


def create_record_store_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the Let It Be Records interior background."""
    surface = pygame.Surface(size)
    w, h = size

    # Warm interior gradient
    create_gradient(surface, [
        (50, 30, 70),
        (70, 45, 100),
        (40, 25, 55),
    ])

    # Floor
    floor_y = h - 50
    pygame.draw.rect(surface, (60, 50, 45), (0, floor_y, w, 55))

    # Floor boards
    for i in range(0, w, 20):
        pygame.draw.line(surface, (50, 40, 35), (i, floor_y), (i, h), 1)

    # Wood grain detail
    for i in range(5):
        pygame.draw.line(surface, (70, 60, 55), (0, floor_y + 10 + i * 10), (w, floor_y + 8 + i * 10))

    # === BACK WALL ===
    wall_y = 30
    pygame.draw.rect(surface, (80, 70, 100), (0, wall_y, w, floor_y - wall_y))

    # Posters on wall
    poster_data = [
        (20, 45, (255, 200, 80), "PRINCE"),
        (60, 40, (200, 100, 150), "HUSKER DU"),
        (100, 50, (100, 200, 255), "REPLACEMENTS"),
        (220, 42, (255, 150, 100), "SUBURBS"),
        (270, 48, (150, 255, 150), "SOUL ASYLUM"),
    ]

    for px, py, color, name in poster_data:
        pygame.draw.rect(surface, color, (px, py, 35, 45))
        pygame.draw.rect(surface, (30, 30, 40), (px, py, 35, 45), 1)
        # Band image suggestion
        pygame.draw.rect(surface, tuple(c - 50 for c in color), (px + 4, py + 5, 27, 25))

    # === RECORD BINS ===
    bin_y = floor_y - 50

    # Front bins
    for bx in [30, 100, 170, 240]:
        pygame.draw.rect(surface, (50, 40, 55), (bx, bin_y, 55, 50))
        pygame.draw.rect(surface, (60, 50, 65), (bx, bin_y, 55, 5))
        # Records in bin
        for i in range(8):
            rx = bx + 5 + i * 6
            color = random.choice([
                (200, 180, 160), (180, 160, 140), (220, 200, 180),
                (160, 180, 200), (200, 160, 180)
            ])
            pygame.draw.rect(surface, color, (rx, bin_y + 8, 4, 38))

    # === COUNTER ===
    counter_x = w - 90
    pygame.draw.rect(surface, (70, 55, 65), (counter_x, floor_y - 45, 80, 45))
    pygame.draw.rect(surface, (90, 75, 85), (counter_x, floor_y - 45, 80, 5))

    # Cash register
    pygame.draw.rect(surface, (50, 50, 55), (counter_x + 20, floor_y - 65, 30, 20))
    pygame.draw.rect(surface, (40, 40, 45), (counter_x + 22, floor_y - 63, 26, 12))

    # === LISTENING BOOTH ===
    booth_x = 10
    pygame.draw.rect(surface, (40, 35, 55), (booth_x, floor_y - 90, 60, 90))
    pygame.draw.rect(surface, (60, 50, 75), (booth_x, floor_y - 90, 60, 5))

    # Headphones on hook
    pygame.draw.arc(surface, (80, 80, 90), (booth_x + 20, floor_y - 80, 20, 15),
                   0, math.pi, 2)
    pygame.draw.rect(surface, (70, 70, 80), (booth_x + 18, floor_y - 73, 6, 8))
    pygame.draw.rect(surface, (70, 70, 80), (booth_x + 36, floor_y - 73, 6, 8))

    # === NEON SIGNS ===
    draw_neon_sign(surface, "VINYL", (140, 35), (255, 100, 200), 16)

    # === ENTRANCE ===
    pygame.draw.rect(surface, (20, 20, 30), (0, floor_y - 80, 25, 80))
    # Glass with street view hint
    pygame.draw.rect(surface, (40, 30, 60), (2, floor_y - 78, 21, 75))

    return surface


def create_radio_station_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the KJRR basement radio station background."""
    surface = pygame.Surface(size)
    w, h = size

    # Cool basement tones
    create_gradient(surface, [
        (20, 35, 55),
        (35, 60, 90),
        (15, 25, 40),
    ])

    # Concrete floor
    floor_y = h - 45
    pygame.draw.rect(surface, (50, 55, 60), (0, floor_y, w, 50))
    # Floor cracks
    pygame.draw.line(surface, (40, 45, 50), (50, floor_y + 10), (100, h), 1)
    pygame.draw.line(surface, (40, 45, 50), (200, floor_y + 5), (180, h), 1)

    # Cinderblock wall
    wall_y = 25
    block_color = (55, 60, 70)
    block_highlight = (65, 70, 80)
    block_w, block_h = 24, 12

    for row in range(10):
        offset = (row % 2) * (block_w // 2)
        for col in range(-1, w // block_w + 2):
            bx = col * block_w + offset
            by = wall_y + row * block_h
            pygame.draw.rect(surface, block_color, (bx, by, block_w - 1, block_h - 1))
            pygame.draw.rect(surface, block_highlight, (bx, by, block_w - 1, 2))

    # === ON AIR LIGHT ===
    light_x, light_y = 150, 45
    pygame.draw.rect(surface, (40, 40, 50), (light_x - 5, light_y - 5, 50, 25))
    pygame.draw.rect(surface, (255, 50, 50), (light_x, light_y, 40, 15))
    # Glow
    for i in range(4):
        alpha = 100 - i * 25
        pygame.draw.rect(surface, (255, 50, 50),
                        (light_x - i * 2, light_y - i * 2, 40 + i * 4, 15 + i * 4), 1)

    # "ON AIR" text
    try:
        font = pygame.font.Font(None, 12)
        text = font.render("ON AIR", True, (255, 255, 255))
        surface.blit(text, (light_x + 5, light_y + 2))
    except:
        pass

    # === DJ BOOTH ===
    booth_x = w - 100
    # Desk
    pygame.draw.rect(surface, (50, 45, 60), (booth_x, floor_y - 50, 90, 50))
    pygame.draw.rect(surface, (60, 55, 70), (booth_x, floor_y - 50, 90, 5))

    # Mixing console
    pygame.draw.rect(surface, (35, 35, 45), (booth_x + 10, floor_y - 70, 70, 25))
    pygame.draw.rect(surface, (30, 30, 40), (booth_x + 12, floor_y - 68, 66, 20))
    # Sliders
    for i in range(8):
        sx = booth_x + 15 + i * 8
        pygame.draw.rect(surface, (80, 80, 90), (sx, floor_y - 65, 4, 15))
        # Slider position
        sy = floor_y - 60 + random.randint(-5, 5)
        pygame.draw.rect(surface, (200, 180, 100), (sx, sy, 4, 3))

    # Turntables
    for tx in [booth_x + 15, booth_x + 55]:
        pygame.draw.circle(surface, (30, 30, 35), (tx + 12, floor_y - 40), 12)
        pygame.draw.circle(surface, (50, 50, 55), (tx + 12, floor_y - 40), 8)
        pygame.draw.circle(surface, (100, 100, 110), (tx + 12, floor_y - 40), 3)

    # === EQUIPMENT RACK ===
    rack_x = 30
    pygame.draw.rect(surface, (40, 40, 50), (rack_x, floor_y - 100, 60, 100))

    # Rack units with blinking lights
    for i in range(5):
        ry = floor_y - 95 + i * 18
        pygame.draw.rect(surface, (30, 30, 40), (rack_x + 5, ry, 50, 15))
        # LED indicators
        for j in range(4):
            led_color = random.choice([(50, 255, 50), (255, 50, 50), (255, 200, 50)])
            pygame.draw.circle(surface, led_color, (rack_x + 12 + j * 12, ry + 7), 2)

    # === CASSETTE STACKS ===
    for sx in [100, 120, 140]:
        stack_h = random.randint(20, 40)
        for i in range(stack_h // 5):
            pygame.draw.rect(surface, (60, 50, 70), (sx, floor_y - 20 - i * 5, 15, 4))

    # === POSTERS ===
    poster_x = 5
    pygame.draw.rect(surface, (200, 150, 100), (poster_x, 50, 30, 40))
    pygame.draw.rect(surface, (20, 20, 30), (poster_x, 50, 30, 40), 1)

    # === DOOR ===
    pygame.draw.rect(surface, (35, 35, 45), (0, floor_y - 75, 22, 75))
    pygame.draw.rect(surface, (45, 45, 55), (2, floor_y - 73, 18, 71))

    return surface


def create_backstage_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the First Avenue backstage area background."""
    surface = pygame.Surface(size)
    w, h = size

    # Warm stage lighting gradient
    create_gradient(surface, [
        (40, 20, 60),
        (70, 40, 100),
        (50, 30, 70),
    ])

    # Floor
    floor_y = h - 50
    pygame.draw.rect(surface, (35, 30, 45), (0, floor_y, w, 55))

    # Stage floor boards
    for i in range(0, w, 15):
        pygame.draw.line(surface, (45, 40, 55), (i, floor_y), (i, h), 1)

    # === STAGE CURTAIN (partially visible) ===
    curtain_color = (120, 20, 40)
    curtain_shadow = (80, 15, 30)
    for i in range(0, 60, 8):
        pygame.draw.rect(surface, curtain_color if i % 16 == 0 else curtain_shadow,
                        (w - 60 + i, 20, 8, floor_y - 20))

    # === MAKEUP MIRRORS ===
    for mx in [30, 90]:
        # Mirror frame
        pygame.draw.rect(surface, (70, 60, 80), (mx, 35, 45, 55))
        pygame.draw.rect(surface, (200, 190, 180), (mx + 3, 38, 39, 49))

        # Mirror bulbs
        for i in range(5):
            by = 40 + i * 10
            pygame.draw.circle(surface, (255, 240, 200), (mx + 5, by), 3)
            pygame.draw.circle(surface, (255, 240, 200), (mx + 40, by), 3)
            # Glow
            pygame.draw.circle(surface, (255, 240, 200), (mx + 5, by), 5)
            pygame.draw.circle(surface, (255, 240, 200), (mx + 40, by), 5)

    # Counter under mirrors
    pygame.draw.rect(surface, (50, 45, 60), (25, floor_y - 35, 120, 35))
    pygame.draw.rect(surface, (60, 55, 70), (25, floor_y - 35, 120, 3))

    # Makeup items on counter
    for i in range(6):
        item_x = 35 + i * 18
        item_color = random.choice([
            (200, 50, 50), (50, 200, 50), (200, 200, 50),
            (150, 150, 200), (200, 100, 150)
        ])
        item_h = random.randint(8, 15)
        pygame.draw.rect(surface, item_color, (item_x, floor_y - 37 - item_h, 8, item_h))

    # === FLIGHT CASES / EQUIPMENT ===
    case_x = 165
    for i, case_h in enumerate([45, 35, 50]):
        cy = floor_y - case_h
        pygame.draw.rect(surface, (30, 30, 35), (case_x + i * 35, cy, 30, case_h))
        pygame.draw.rect(surface, (50, 50, 55), (case_x + i * 35, cy, 30, 3))
        # Latches
        pygame.draw.rect(surface, (150, 140, 100), (case_x + i * 35 + 12, cy + case_h - 8, 6, 4))

    # === SETLIST CRATE ===
    crate_x = 40
    pygame.draw.rect(surface, (70, 60, 50), (crate_x, floor_y - 40, 50, 40))
    pygame.draw.rect(surface, (80, 70, 60), (crate_x, floor_y - 40, 50, 4))

    # Papers sticking out
    for i in range(4):
        paper_x = crate_x + 8 + i * 10
        paper_color = (240, 235, 225)
        pygame.draw.rect(surface, paper_color, (paper_x, floor_y - 50, 8, 15))

    # === MONITOR MIX CONSOLE ===
    console_x = w // 2 - 30
    pygame.draw.rect(surface, (40, 40, 50), (console_x, floor_y - 55, 60, 55))
    pygame.draw.rect(surface, (35, 35, 45), (console_x + 5, floor_y - 50, 50, 40))

    # Knobs and faders
    for row in range(3):
        for col in range(5):
            kx = console_x + 10 + col * 10
            ky = floor_y - 45 + row * 12
            pygame.draw.circle(surface, (80, 80, 90), (kx, ky), 3)
            # Indicator
            pygame.draw.circle(surface, (200, 200, 100), (kx, ky - 2), 1)

    # VU meters
    for i in range(2):
        pygame.draw.rect(surface, (30, 30, 35), (console_x + 20 + i * 15, floor_y - 65, 10, 12))
        # Meter level
        level = random.randint(3, 10)
        pygame.draw.rect(surface, (50, 255, 50), (console_x + 22 + i * 15, floor_y - 55 - level, 6, level))

    # === STAGE DOOR ===
    door_x = w - 35
    pygame.draw.rect(surface, (50, 45, 60), (door_x, floor_y - 80, 30, 80))
    pygame.draw.rect(surface, (40, 35, 50), (door_x + 3, floor_y - 77, 24, 74))

    # Exit sign
    pygame.draw.rect(surface, (255, 50, 50), (door_x + 5, floor_y - 95, 20, 10))
    try:
        font = pygame.font.Font(None, 10)
        exit_text = font.render("EXIT", True, (255, 255, 255))
        surface.blit(exit_text, (door_x + 7, floor_y - 94))
    except:
        pass

    # === CABLES ON FLOOR ===
    cable_points = [(50, h - 30), (100, h - 25), (150, h - 35), (200, h - 28)]
    pygame.draw.lines(surface, (30, 30, 35), False, cable_points, 3)

    # === INSTRUMENTS IN CORNER ===
    # Guitar case
    pygame.draw.ellipse(surface, (50, 40, 35), (5, floor_y - 25, 15, 50))
    pygame.draw.ellipse(surface, (40, 30, 25), (7, floor_y - 23, 11, 46))

    return surface


def create_green_room_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the green room background with band hangout atmosphere."""
    surface = pygame.Surface(size)
    w, h = size

    # Moody green-tinted gradient
    create_gradient(surface, [
        (20, 45, 35),
        (40, 80, 60),
        (15, 35, 25),
    ])

    # Floor - worn carpet
    floor_y = h - 45
    pygame.draw.rect(surface, (50, 65, 55), (0, floor_y, w, 50))
    # Carpet texture
    for i in range(20):
        cx = random.randint(0, w)
        cy = random.randint(floor_y, h)
        pygame.draw.circle(surface, (55, 70, 60), (cx, cy), 2)

    # === BACK WALL ===
    wall_color = (45, 60, 50)
    pygame.draw.rect(surface, wall_color, (0, 20, w, floor_y - 20))

    # Wood paneling detail
    for i in range(0, w, 40):
        pygame.draw.line(surface, (40, 55, 45), (i, 20), (i, floor_y), 2)

    # === VINTAGE COUCH ===
    couch_x = 20
    couch_w = 90
    couch_h = 40
    couch_y = floor_y - couch_h

    # Couch back
    pygame.draw.rect(surface, (80, 50, 40), (couch_x, couch_y - 25, couch_w, 30))
    pygame.draw.rect(surface, (70, 45, 35), (couch_x + 5, couch_y - 20, couch_w - 10, 20))

    # Couch seat
    pygame.draw.rect(surface, (90, 55, 45), (couch_x, couch_y, couch_w, couch_h))
    # Cushion lines
    pygame.draw.line(surface, (75, 45, 35), (couch_x + 30, couch_y), (couch_x + 30, couch_y + couch_h), 2)
    pygame.draw.line(surface, (75, 45, 35), (couch_x + 60, couch_y), (couch_x + 60, couch_y + couch_h), 2)

    # Couch legs
    pygame.draw.rect(surface, (50, 40, 30), (couch_x + 5, floor_y - 5, 8, 8))
    pygame.draw.rect(surface, (50, 40, 30), (couch_x + couch_w - 13, floor_y - 5, 8, 8))

    # === COFFEE TABLE ===
    table_x = 60
    pygame.draw.rect(surface, (60, 50, 40), (table_x, floor_y - 20, 45, 18))
    pygame.draw.rect(surface, (70, 60, 50), (table_x, floor_y - 20, 45, 3))

    # Coffee cups
    pygame.draw.ellipse(surface, (200, 200, 200), (table_x + 10, floor_y - 25, 8, 5))
    pygame.draw.ellipse(surface, (150, 100, 80), (table_x + 30, floor_y - 25, 8, 5))

    # === DELI TRAY ===
    tray_x = 140
    pygame.draw.rect(surface, (180, 180, 190), (tray_x, floor_y - 50, 50, 35))
    pygame.draw.rect(surface, (160, 160, 170), (tray_x + 2, floor_y - 48, 46, 31))
    # Food items
    food_colors = [(180, 100, 100), (255, 220, 100), (150, 200, 150), (200, 150, 100)]
    for i, color in enumerate(food_colors):
        fx = tray_x + 8 + (i % 2) * 20
        fy = floor_y - 45 + (i // 2) * 15
        pygame.draw.rect(surface, color, (fx, fy, 15, 12))

    # === POSTER WALL ===
    posters = [
        (200, 35, (255, 180, 80), "PRINCE"),
        (240, 40, (200, 100, 200), "THE CURE"),
        (280, 35, (100, 200, 255), "NEW ORDER"),
    ]
    for px, py, color, _ in posters:
        pygame.draw.rect(surface, color, (px, py, 35, 45))
        pygame.draw.rect(surface, (30, 30, 40), (px, py, 35, 45), 1)
        pygame.draw.rect(surface, tuple(c - 50 for c in color), (px + 4, py + 5, 27, 25))

    # === GUITAR RACK ===
    rack_x = 10
    pygame.draw.rect(surface, (60, 50, 40), (rack_x, floor_y - 90, 35, 90))
    pygame.draw.rect(surface, (50, 40, 30), (rack_x + 3, floor_y - 87, 29, 84))

    # Guitars
    guitar_colors = [(180, 50, 50), (50, 50, 50), (200, 150, 80)]
    for i, gc in enumerate(guitar_colors):
        gy = floor_y - 80 + i * 25
        # Neck
        pygame.draw.rect(surface, (80, 60, 40), (rack_x + 8, gy, 20, 4))
        # Body
        pygame.draw.ellipse(surface, gc, (rack_x + 5, gy + 2, 12, 18))
        pygame.draw.ellipse(surface, gc, (rack_x + 12, gy + 2, 14, 20))

    # === RECORD CRATE ===
    crate_x = 180
    pygame.draw.rect(surface, (70, 60, 50), (crate_x, floor_y - 30, 50, 30))
    pygame.draw.rect(surface, (60, 50, 40), (crate_x + 2, floor_y - 28, 46, 26))
    # Records in crate
    for i in range(6):
        r_color = random.choice([(30, 30, 30), (40, 35, 35), (35, 35, 40)])
        pygame.draw.rect(surface, r_color, (crate_x + 5 + i * 7, floor_y - 26, 5, 22))

    # === DOOR TO BACKSTAGE ===
    door_x = w - 35
    pygame.draw.rect(surface, (55, 50, 45), (door_x, floor_y - 80, 30, 80))
    pygame.draw.rect(surface, (45, 40, 35), (door_x + 3, floor_y - 77, 24, 74))
    # Door handle
    pygame.draw.circle(surface, (150, 130, 100), (door_x + 22, floor_y - 40), 3)

    # === LAMP ===
    lamp_x = 130
    # Lamp base
    pygame.draw.rect(surface, (60, 50, 40), (lamp_x, floor_y - 15, 15, 15))
    # Lamp pole
    pygame.draw.rect(surface, (80, 70, 50), (lamp_x + 6, floor_y - 60, 3, 45))
    # Lamp shade
    pygame.draw.polygon(surface, (200, 180, 150), [
        (lamp_x - 5, floor_y - 60),
        (lamp_x + 20, floor_y - 60),
        (lamp_x + 15, floor_y - 75),
        (lamp_x, floor_y - 75),
    ])
    # Light glow
    for i in range(3):
        pygame.draw.circle(surface, (255, 240, 200), (lamp_x + 7, floor_y - 55), 10 + i * 5)

    # === CABLES AND CLUTTER ===
    cable_points = [(50, h - 20), (90, h - 25), (130, h - 18)]
    pygame.draw.lines(surface, (30, 35, 30), False, cable_points, 2)

    # Magazines on floor
    pygame.draw.rect(surface, (200, 180, 160), (95, floor_y - 5, 12, 8))
    pygame.draw.rect(surface, (180, 160, 200), (100, floor_y - 3, 12, 8))

    return surface


def get_room_background(room_id: str, size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Get the appropriate background for a room ID."""
    generators = {
        "hennepin_outside": create_hennepin_background,
        "record_store": create_record_store_background,
        "college_station": create_radio_station_background,
        "backstage_stage": create_backstage_background,
        "green_room": create_green_room_background,
    }

    generator = generators.get(room_id)
    if generator:
        return generator(size)

    # Default background
    surface = pygame.Surface(size)
    create_gradient(surface, [(30, 20, 50), (60, 40, 90), (20, 15, 35)])
    return surface
