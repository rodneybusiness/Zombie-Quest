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


def create_merch_booth_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the merch booth with t-shirts, posters, buttons, and collectibles."""
    surface = pygame.Surface(size)
    w, h = size

    # Warm booth lighting gradient
    create_gradient(surface, [
        (35, 25, 55),
        (60, 45, 90),
        (30, 20, 45),
    ])

    # Floor
    floor_y = h - 50
    pygame.draw.rect(surface, (40, 35, 50), (0, floor_y, w, 55))

    # Floor scuffs and wear marks
    for i in range(10):
        sx = random.randint(0, w)
        sy = random.randint(floor_y, h)
        pygame.draw.circle(surface, (35, 30, 45), (sx, sy), random.randint(2, 4))

    # === BACK WALL ===
    wall_y = 25
    pygame.draw.rect(surface, (50, 45, 70), (0, wall_y, w, floor_y - wall_y))

    # === MERCH DISPLAY RACKS ===
    # Left rack - T-shirts hanging
    rack_x = 25
    pygame.draw.rect(surface, (60, 55, 70), (rack_x, 45, 80, 100))
    pygame.draw.rect(surface, (70, 65, 80), (rack_x, 45, 80, 5))

    # T-shirts on hangers
    shirt_colors = [
        (0, 0, 0),        # Black
        (180, 180, 180),  # Gray
        (150, 30, 30),    # Red
        (30, 30, 150),    # Blue
        (255, 200, 50),   # Yellow
    ]
    for i, color in enumerate(shirt_colors):
        sx = rack_x + 8 + i * 14
        sy = 52
        # Hanger
        pygame.draw.line(surface, (150, 140, 120), (sx + 5, sy), (sx + 8, sy - 3), 1)
        pygame.draw.line(surface, (150, 140, 120), (sx + 8, sy - 3), (sx + 11, sy), 1)
        # Shirt body
        pygame.draw.rect(surface, color, (sx + 2, sy + 2, 14, 18))
        # Band logo suggestion
        pygame.draw.rect(surface, tuple(min(255, c + 60) for c in color), (sx + 4, sy + 6, 10, 8))

    # Right rack - Posters
    poster_x = w - 105
    pygame.draw.rect(surface, (55, 50, 65), (poster_x, 40, 75, 110))
    pygame.draw.rect(surface, (65, 60, 75), (poster_x, 40, 75, 5))

    # Posters displayed
    poster_data = [
        (poster_x + 5, 50, (255, 100, 200), "NEON DEAD"),
        (poster_x + 45, 50, (100, 200, 255), "REPLACEMENTS"),
        (poster_x + 5, 90, (255, 200, 80), "PRINCE"),
        (poster_x + 45, 90, (150, 255, 150), "HUSKER DU"),
    ]
    for px, py, color, name in poster_data:
        pygame.draw.rect(surface, color, (px, py, 32, 40))
        pygame.draw.rect(surface, (30, 30, 40), (px, py, 32, 40), 1)
        # Image area
        pygame.draw.rect(surface, tuple(c - 50 for c in color), (px + 3, py + 3, 26, 25))
        # Text lines
        pygame.draw.line(surface, (30, 30, 40), (px + 5, py + 32), (px + 27, py + 32), 1)
        pygame.draw.line(surface, (30, 30, 40), (px + 5, py + 35), (px + 27, py + 35), 1)

    # === MERCH COUNTER ===
    counter_x = w // 2 - 60
    counter_w = 120
    pygame.draw.rect(surface, (55, 50, 65), (counter_x, floor_y - 55, counter_w, 55))
    pygame.draw.rect(surface, (65, 60, 75), (counter_x, floor_y - 55, counter_w, 5))

    # Counter top details
    # Cash box
    pygame.draw.rect(surface, (80, 80, 90), (counter_x + 15, floor_y - 70, 25, 18))
    pygame.draw.rect(surface, (70, 70, 80), (counter_x + 17, floor_y - 68, 21, 14))

    # Button display on counter
    for i in range(12):
        bx = counter_x + 50 + (i % 4) * 12
        by = floor_y - 68 + (i // 4) * 12
        button_color = random.choice([
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255)
        ])
        pygame.draw.circle(surface, button_color, (bx, by), 4)
        pygame.draw.circle(surface, (255, 255, 255), (bx, by), 2)

    # Price signs
    pygame.draw.rect(surface, (240, 240, 240), (counter_x + 95, floor_y - 68, 20, 12))
    try:
        font = pygame.font.Font(None, 10)
        price = font.render("$5", True, (0, 0, 0))
        surface.blit(price, (counter_x + 100, floor_y - 66))
    except:
        pass

    # === DISPLAY SHELF ===
    shelf_x = 130
    pygame.draw.rect(surface, (65, 60, 75), (shelf_x, floor_y - 35, 60, 4))

    # Collectible items on shelf
    items = [
        ((200, 150, 50), 8, 15),   # Cassette
        ((150, 150, 160), 10, 12), # Pin collection
        ((255, 200, 180), 12, 10), # Stickers
    ]
    for i, (color, w_item, h_item) in enumerate(items):
        ix = shelf_x + 8 + i * 18
        pygame.draw.rect(surface, color, (ix, floor_y - 35 - h_item, w_item, h_item))

    # === NEON SIGNS ===
    draw_neon_sign(surface, "MERCH", (115, 30), (255, 100, 200), 18)

    # Band stickers on wall
    for i in range(8):
        stx = 140 + i * 20
        sty = 130 + random.randint(-10, 10)
        sticker_color = random.choice([
            (255, 100, 100), (100, 255, 100), (255, 255, 100), (100, 200, 255)
        ])
        pygame.draw.rect(surface, sticker_color, (stx, sty, 15, 8))

    # === ENTRANCE ===
    pygame.draw.rect(surface, (25, 20, 35), (0, floor_y - 75, 22, 75))

    return surface


def create_coat_check_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the claustrophobic coat check room with hundreds of coats."""
    surface = pygame.Surface(size)
    w, h = size

    # Dim, cramped gradient
    create_gradient(surface, [
        (25, 20, 35),
        (45, 35, 60),
        (20, 15, 30),
    ])

    # Floor - worn linoleum
    floor_y = h - 45
    pygame.draw.rect(surface, (45, 40, 50), (0, floor_y, w, 50))

    # Floor tiles pattern
    for tx in range(0, w, 20):
        for ty in range(floor_y, h, 20):
            pygame.draw.rect(surface, (40, 35, 45), (tx, ty, 20, 20), 1)

    # === COAT RACKS - Left side ===
    rack_h = 120
    for rack_num in range(2):
        rack_x = 15 + rack_num * 70
        # Rack structure
        pygame.draw.rect(surface, (50, 45, 55), (rack_x, floor_y - rack_h, 50, rack_h))
        pygame.draw.rect(surface, (60, 55, 65), (rack_x, floor_y - rack_h, 50, 3))

        # Hangers and coats
        coat_colors = [
            (30, 30, 35), (60, 55, 50), (80, 70, 60), (40, 45, 50),
            (70, 60, 55), (50, 50, 55), (35, 35, 40)
        ]
        for i, coat_color in enumerate(coat_colors):
            hx = rack_x + 5 + i * 6
            hy = floor_y - rack_h + 8
            # Hanger
            pygame.draw.line(surface, (150, 140, 130), (hx + 2, hy), (hx + 3, hy - 2), 1)
            # Coat hanging
            coat_h = random.randint(40, 60)
            pygame.draw.rect(surface, coat_color, (hx, hy + 2, 5, coat_h))
            # Coat details
            pygame.draw.line(surface, tuple(c + 10 for c in coat_color), (hx + 2, hy + 5), (hx + 2, hy + coat_h - 5), 1)

    # === COAT RACKS - Right side ===
    rack_x_right = w - 95
    pygame.draw.rect(surface, (50, 45, 55), (rack_x_right, floor_y - rack_h, 85, rack_h))
    pygame.draw.rect(surface, (60, 55, 65), (rack_x_right, floor_y - rack_h, 85, 3))

    # Dense coat hanging
    for i in range(14):
        hx = rack_x_right + 5 + i * 6
        hy = floor_y - rack_h + 8
        coat_color = random.choice([
            (30, 30, 35), (60, 55, 50), (80, 70, 60), (40, 45, 50),
            (50, 40, 45), (70, 65, 60), (35, 35, 40), (45, 50, 55)
        ])
        coat_h = random.randint(45, 65)
        pygame.draw.rect(surface, coat_color, (hx, hy + 2, 5, coat_h))

    # === COUNTER ===
    counter_x = w // 2 - 50
    pygame.draw.rect(surface, (60, 55, 65), (counter_x, floor_y - 50, 100, 50))
    pygame.draw.rect(surface, (70, 65, 75), (counter_x, floor_y - 50, 100, 4))

    # Coat check tickets scattered
    for i in range(6):
        tx = counter_x + 10 + i * 14
        ty = floor_y - 48 + random.randint(-3, 3)
        pygame.draw.rect(surface, (240, 230, 210), (tx, ty, 10, 6))
        # Number on ticket
        pygame.draw.rect(surface, (30, 30, 30), (tx + 2, ty + 1, 2, 3))

    # Lost and found box
    pygame.draw.rect(surface, (70, 60, 50), (counter_x + 70, floor_y - 45, 25, 20))
    pygame.draw.rect(surface, (60, 50, 40), (counter_x + 72, floor_y - 43, 21, 16))

    # Items in lost and found
    lost_items = [(255, 200, 50), (200, 100, 100), (100, 150, 200)]
    for i, color in enumerate(lost_items):
        ix = counter_x + 75 + i * 6
        pygame.draw.rect(surface, color, (ix, floor_y - 40, 5, 8))

    # === OVERHEAD SIGN ===
    pygame.draw.rect(surface, (80, 75, 90), (w // 2 - 40, 35, 80, 20))
    draw_neon_sign(surface, "COAT CHECK", (w // 2 - 35, 40), (200, 255, 200), 12)

    # === HIDDEN PASSAGE HINT ===
    # Dark gap behind coats on left
    pygame.draw.rect(surface, (10, 8, 15), (8, floor_y - 90, 12, 60))
    # Mystery items visible in gap
    pygame.draw.circle(surface, (100, 100, 120), (14, floor_y - 60), 3)

    # === DUSTY ATMOSPHERE ===
    # Dust particles
    for i in range(25):
        dx = random.randint(0, w)
        dy = random.randint(30, floor_y)
        pygame.draw.circle(surface, (80, 75, 90), (dx, dy), 1)

    # === DOOR ===
    door_x = w - 30
    pygame.draw.rect(surface, (40, 35, 45), (door_x, floor_y - 70, 25, 70))
    pygame.draw.rect(surface, (50, 45, 55), (door_x + 2, floor_y - 68, 21, 66))

    return surface


def create_sound_booth_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the sound booth with massive mixing console and stage view."""
    surface = pygame.Surface(size)
    w, h = size

    # Technical room gradient
    create_gradient(surface, [
        (20, 25, 35),
        (35, 45, 65),
        (15, 20, 30),
    ])

    # Floor
    floor_y = h - 40
    pygame.draw.rect(surface, (35, 40, 50), (0, floor_y, w, 45))

    # === VIEWING WINDOW TO STAGE ===
    window_y = 35
    window_h = 70
    # Window frame
    pygame.draw.rect(surface, (50, 50, 60), (10, window_y, w - 20, window_h))
    # Glass
    pygame.draw.rect(surface, (30, 25, 45), (15, window_y + 5, w - 30, window_h - 10))

    # Stage view through glass - silhouettes and lights
    # Stage lights
    for i in range(5):
        lx = 30 + i * 50
        ly = window_y + 15
        light_color = random.choice([
            (255, 100, 100), (100, 100, 255), (100, 255, 100),
            (255, 255, 100), (255, 100, 255)
        ])
        pygame.draw.circle(surface, light_color, (lx, ly), 8)
        # Beam
        for j in range(3):
            beam_alpha = 60 - j * 20
            pygame.draw.line(surface, light_color, (lx, ly + 8), (lx - 10 + j * 10, window_y + window_h - 5), 2)

    # Band silhouettes on stage
    pygame.draw.rect(surface, (15, 10, 25), (40, window_y + 50, 15, 25))
    pygame.draw.circle(surface, (15, 10, 25), (47, window_y + 48), 6)
    pygame.draw.rect(surface, (15, 10, 25), (80, window_y + 48, 15, 27))
    pygame.draw.circle(surface, (15, 10, 25), (87, window_y + 46), 6)

    # === MASSIVE MIXING CONSOLE ===
    console_y = floor_y - 100
    console_h = 100
    console_w = w - 40

    # Console main body
    pygame.draw.rect(surface, (40, 40, 50), (20, console_y, console_w, console_h))
    pygame.draw.rect(surface, (35, 35, 45), (25, console_y + 5, console_w - 10, console_h - 10))

    # Slanted control surface
    pygame.draw.polygon(surface, (45, 45, 55), [
        (25, console_y + 20),
        (console_w + 15, console_y + 20),
        (console_w + 10, console_y + 70),
        (30, console_y + 70)
    ])

    # Channel strips - LOTS of them
    num_channels = 24
    channel_w = (console_w - 20) // num_channels

    for i in range(num_channels):
        cx = 30 + i * channel_w
        cy = console_y + 25

        # Fader slot
        pygame.draw.rect(surface, (30, 30, 35), (cx + 1, cy + 5, channel_w - 3, 35))

        # Fader position (random)
        fader_pos = random.randint(8, 30)
        pygame.draw.rect(surface, (200, 180, 100), (cx + 1, cy + 5 + fader_pos, channel_w - 3, 4))

        # Knob above fader
        knob_y = cy - 5
        pygame.draw.circle(surface, (60, 60, 70), (cx + channel_w // 2, knob_y), 3)
        # Knob indicator
        angle = random.uniform(0, math.pi * 2)
        ind_x = cx + channel_w // 2 + int(2 * math.cos(angle))
        ind_y = knob_y + int(2 * math.sin(angle))
        pygame.draw.circle(surface, (255, 200, 100), (ind_x, ind_y), 1)

    # === VU METERS ===
    meter_y = console_y - 25
    for i in range(8):
        mx = 40 + i * 35
        # Meter housing
        pygame.draw.rect(surface, (30, 30, 35), (mx, meter_y, 25, 18))
        # Meter level (random)
        level = random.randint(5, 22)
        # Green section
        if level > 5:
            pygame.draw.rect(surface, (50, 255, 50), (mx + 2, meter_y + 16 - min(level, 12), 21, min(level, 12)))
        # Yellow section
        if level > 12:
            pygame.draw.rect(surface, (255, 255, 50), (mx + 2, meter_y + 16 - min(level, 18), 21, min(level - 12, 6)))
        # Red section
        if level > 18:
            pygame.draw.rect(surface, (255, 50, 50), (mx + 2, meter_y + 16 - (level - 18), 21, level - 18))

    # === MASTER SECTION ===
    master_x = console_w - 50
    # Master fader
    pygame.draw.rect(surface, (80, 80, 90), (master_x, console_y + 30, 35, 50))
    pygame.draw.rect(surface, (30, 30, 35), (master_x + 2, console_y + 32, 31, 46))
    pygame.draw.rect(surface, (255, 200, 100), (master_x + 2, console_y + 52, 31, 6))

    # === EQUIPMENT ON DESK ===
    # Headphones
    phones_x = 80
    pygame.draw.arc(surface, (70, 70, 80), (phones_x, floor_y - 115, 30, 20), 0, math.pi, 3)
    pygame.draw.rect(surface, (60, 60, 70), (phones_x + 5, floor_y - 105, 8, 10))
    pygame.draw.rect(surface, (60, 60, 70), (phones_x + 17, floor_y - 105, 8, 10))

    # Coffee cup
    pygame.draw.ellipse(surface, (200, 180, 160), (140, floor_y - 108, 12, 8))
    pygame.draw.rect(surface, (200, 180, 160), (140, floor_y - 115, 12, 10))
    # Coffee inside
    pygame.draw.ellipse(surface, (80, 60, 40), (142, floor_y - 113, 8, 4))

    # Notepad
    pygame.draw.rect(surface, (240, 230, 210), (180, floor_y - 110, 25, 18))
    # Notes on pad
    for i in range(4):
        pygame.draw.line(surface, (100, 100, 120), (183, floor_y - 106 + i * 4), (200, floor_y - 106 + i * 4), 1)

    # === SPEAKER MONITORS ===
    # Left speaker
    pygame.draw.rect(surface, (30, 30, 35), (5, floor_y - 70, 25, 35))
    pygame.draw.circle(surface, (50, 50, 55), (17, floor_y - 60), 8)
    pygame.draw.circle(surface, (60, 60, 65), (17, floor_y - 45), 6)

    # Right speaker
    pygame.draw.rect(surface, (30, 30, 35), (w - 30, floor_y - 70, 25, 35))
    pygame.draw.circle(surface, (50, 50, 55), (w - 18, floor_y - 60), 8)
    pygame.draw.circle(surface, (60, 60, 65), (w - 18, floor_y - 45), 6)

    # === DOOR ===
    door_x = w - 28
    pygame.draw.rect(surface, (35, 35, 45), (door_x, floor_y - 65, 22, 65))

    return surface


def create_vip_lounge_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the VIP lounge with luxury and dark secrets."""
    surface = pygame.Surface(size)
    w, h = size

    # Moody luxury gradient - deep purples and reds
    create_gradient(surface, [
        (40, 20, 50),
        (70, 35, 80),
        (30, 15, 40),
    ])

    # Floor - plush carpet
    floor_y = h - 50
    pygame.draw.rect(surface, (60, 30, 45), (0, floor_y, w, 55))

    # Carpet pattern
    for i in range(0, w, 30):
        for j in range(floor_y, h, 30):
            pygame.draw.circle(surface, (55, 25, 40), (i + 15, j + 15), 8)

    # === BACK WALL - Textured ===
    wall_y = 25
    wall_color = (55, 40, 65)
    pygame.draw.rect(surface, wall_color, (0, wall_y, w, floor_y - wall_y))

    # Wallpaper pattern
    for i in range(0, w, 40):
        for j in range(wall_y, floor_y, 40):
            pygame.draw.circle(surface, (50, 35, 60), (i + 20, j + 20), 6)

    # === VELVET COUCHES ===
    # Left couch
    couch_x = 20
    couch_w = 80
    couch_color = (100, 30, 60)  # Deep red velvet

    # Couch back
    pygame.draw.rect(surface, couch_color, (couch_x, floor_y - 60, couch_w, 25))
    pygame.draw.rect(surface, tuple(c - 20 for c in couch_color), (couch_x + 5, floor_y - 55, couch_w - 10, 20))

    # Couch seat
    pygame.draw.rect(surface, couch_color, (couch_x, floor_y - 35, couch_w, 35))
    # Cushion tufting
    for i in range(3):
        for j in range(2):
            tx = couch_x + 15 + i * 25
            ty = floor_y - 28 + j * 15
            pygame.draw.circle(surface, tuple(c - 30 for c in couch_color), (tx, ty), 3)

    # Right couch
    couch_r_x = w - 100
    pygame.draw.rect(surface, couch_color, (couch_r_x, floor_y - 60, couch_w, 25))
    pygame.draw.rect(surface, tuple(c - 20 for c in couch_color), (couch_r_x + 5, floor_y - 55, couch_w - 10, 20))
    pygame.draw.rect(surface, couch_color, (couch_r_x, floor_y - 35, couch_w, 35))

    # === GLASS TABLE ===
    table_x = w // 2 - 40
    # Table top - glass effect
    pygame.draw.rect(surface, (150, 180, 200), (table_x, floor_y - 25, 80, 4))
    pygame.draw.rect(surface, (180, 200, 220), (table_x + 2, floor_y - 25, 76, 2))

    # Table legs
    pygame.draw.rect(surface, (180, 180, 190), (table_x + 5, floor_y - 25, 4, 25))
    pygame.draw.rect(surface, (180, 180, 190), (table_x + 71, floor_y - 25, 4, 25))

    # === CHAMPAGNE AND GLASSES ===
    # Champagne bottle
    pygame.draw.rect(surface, (40, 80, 40), (table_x + 15, floor_y - 50, 8, 25))
    pygame.draw.rect(surface, (30, 60, 30), (table_x + 15, floor_y - 52, 8, 5))
    # Foil
    pygame.draw.rect(surface, (200, 180, 100), (table_x + 15, floor_y - 52, 8, 3))

    # Champagne flutes
    for i in range(3):
        gx = table_x + 35 + i * 15
        # Glass bowl
        pygame.draw.polygon(surface, (200, 220, 240), [
            (gx + 3, floor_y - 35),
            (gx + 6, floor_y - 35),
            (gx + 5, floor_y - 42),
            (gx + 4, floor_y - 42)
        ])
        # Stem
        pygame.draw.rect(surface, (180, 200, 220), (gx + 4, floor_y - 35, 1, 8))
        # Base
        pygame.draw.line(surface, (180, 200, 220), (gx + 2, floor_y - 27), (gx + 6, floor_y - 27), 1)
        # Bubbles in glass
        if i == 0:
            pygame.draw.circle(surface, (255, 255, 200), (gx + 4, floor_y - 38), 1)

    # === MOOD LIGHTING ===
    # Wall sconces
    for sx in [60, 180, 260]:
        # Sconce fixture
        pygame.draw.rect(surface, (150, 130, 100), (sx, 50, 12, 18))
        pygame.draw.polygon(surface, (200, 180, 140), [
            (sx + 2, 50),
            (sx + 10, 50),
            (sx + 12, 42),
            (sx, 42)
        ])
        # Light glow
        for i in range(4):
            alpha = 100 - i * 25
            pygame.draw.circle(surface, (255, 240, 200), (sx + 6, 45), 10 + i * 3)

    # === LUXURY DETAILS ===
    # Bar cart
    cart_x = 115
    pygame.draw.rect(surface, (150, 130, 100), (cart_x, floor_y - 55, 45, 55))
    pygame.draw.rect(surface, (180, 160, 130), (cart_x + 2, floor_y - 53, 41, 3))

    # Liquor bottles
    bottle_colors = [(180, 100, 50), (200, 150, 100), (100, 80, 60)]
    for i, color in enumerate(bottle_colors):
        bx = cart_x + 8 + i * 13
        pygame.draw.rect(surface, color, (bx, floor_y - 75, 8, 20))
        pygame.draw.rect(surface, (30, 30, 30), (bx, floor_y - 77, 8, 4))

    # === VELVET ROPE BARRIER ===
    rope_y = floor_y - 10
    # Stanchions
    pygame.draw.rect(surface, (200, 180, 100), (10, rope_y, 6, 15))
    pygame.draw.rect(surface, (200, 180, 100), (304, rope_y, 6, 15))

    # Rope - use curved line
    points = []
    for i in range(30):
        x = 13 + i * 10
        y = rope_y + 5 + int(8 * math.sin(i * 0.5))
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.lines(surface, (150, 30, 50), False, points, 3)

    # === MYSTERIOUS DOCUMENTS ===
    # Contract on table
    pygame.draw.rect(surface, (240, 230, 210), (table_x + 50, floor_y - 30, 25, 18))
    # Signature line
    pygame.draw.line(surface, (30, 30, 30), (table_x + 53, floor_y - 15), (table_x + 72, floor_y - 15), 1)
    # Blood drop?
    pygame.draw.circle(surface, (150, 30, 30), (table_x + 60, floor_y - 20), 2)

    # === VIP SIGN ===
    sign_x = w // 2 - 30
    pygame.draw.rect(surface, (30, 25, 35), (sign_x, 28, 60, 18))
    draw_neon_sign(surface, "VIP ONLY", (sign_x + 5, 32), (255, 200, 100), 12)

    # === DOOR ===
    door_x = w - 32
    pygame.draw.rect(surface, (50, 35, 45), (door_x, floor_y - 80, 28, 80))
    pygame.draw.rect(surface, (40, 25, 35), (door_x + 3, floor_y - 77, 22, 74))
    # Gold handle
    pygame.draw.circle(surface, (200, 180, 100), (door_x + 22, floor_y - 40), 3)

    return surface


def create_memorial_wall_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the memorial wall honoring Minneapolis musicians."""
    surface = pygame.Surface(size)
    w, h = size

    # Somber, reflective gradient
    create_gradient(surface, [
        (15, 15, 25),
        (30, 30, 45),
        (10, 10, 20),
    ])

    # Floor
    floor_y = h - 45
    pygame.draw.rect(surface, (30, 30, 40), (0, floor_y, w, 50))

    # === THE MEMORIAL WALL ===
    wall_y = 20
    wall_color = (35, 35, 50)
    pygame.draw.rect(surface, wall_color, (0, wall_y, w, floor_y - wall_y))

    # === PHOTO FRAMES - Grid of musicians ===
    photos = [
        # Top row
        (25, 35, (200, 180, 150), "Prince-like silhouette"),
        (70, 35, (180, 200, 190), "Husker Du member"),
        (115, 35, (190, 180, 200), "Replacements"),
        (160, 35, (200, 190, 180), "Soul Asylum"),
        (205, 35, (180, 190, 200), "The Suburbs"),
        (250, 35, (200, 200, 180), "Jayhawks"),
        # Middle row
        (25, 85, (185, 195, 200), "Local legend"),
        (70, 85, (200, 185, 190), "Punk pioneer"),
        (115, 85, (190, 190, 200), "Jazz great"),
        (160, 85, (200, 180, 185), "Blues master"),
        (205, 85, (185, 200, 195), "Folk singer"),
        (250, 85, (195, 185, 200), "Rock icon"),
        # Bottom row
        (47, 135, (200, 190, 185), "Recent loss"),
        (92, 135, (185, 200, 190), "Club regular"),
        (137, 135, (190, 185, 200), "Beloved DJ"),
        (182, 135, (200, 200, 190), "Sound engineer"),
        (227, 135, (190, 195, 200), "Promoter"),
    ]

    for px, py, frame_color, desc in photos:
        # Photo frame
        pygame.draw.rect(surface, frame_color, (px, py, 38, 45))
        pygame.draw.rect(surface, (20, 20, 25), (px + 3, py + 3, 32, 39))

        # Photo content - silhouette suggestion
        silhouette_color = random.choice([
            (40, 40, 50), (45, 45, 55), (35, 35, 45)
        ])
        # Head
        pygame.draw.circle(surface, silhouette_color, (px + 19, py + 16), 6)
        # Shoulders
        pygame.draw.polygon(surface, silhouette_color, [
            (px + 13, py + 22),
            (px + 25, py + 22),
            (px + 28, py + 36),
            (px + 10, py + 36)
        ])

        # Some photos have a glow (indicating they're now zombies in the venue)
        if random.random() > 0.6:
            pygame.draw.rect(surface, (100, 255, 100), (px, py, 38, 45), 1)

    # === CANDLES ON FLOOR ===
    candle_y = floor_y - 35
    for i in range(12):
        cx = 30 + i * 25
        # Candle body
        candle_color = (240, 230, 210)
        pygame.draw.rect(surface, candle_color, (cx, candle_y + 10, 6, 20))
        # Wax drip
        pygame.draw.polygon(surface, candle_color, [
            (cx + 2, candle_y + 15),
            (cx + 1, candle_y + 25),
            (cx + 3, candle_y + 20)
        ])
        # Flame
        pygame.draw.polygon(surface, (255, 200, 50), [
            (cx + 3, candle_y + 5),
            (cx + 1, candle_y + 10),
            (cx + 5, candle_y + 10)
        ])
        # Flame highlight
        pygame.draw.circle(surface, (255, 255, 200), (cx + 3, candle_y + 8), 2)
        # Glow
        for j in range(2):
            pygame.draw.circle(surface, (255, 220, 100), (cx + 3, candle_y + 7), 6 + j * 3)

    # === FLOWER TRIBUTES ===
    flower_clusters = [
        (15, floor_y - 15, (200, 50, 50)),   # Red roses
        (80, floor_y - 18, (255, 255, 255)), # White lilies
        (150, floor_y - 16, (255, 200, 50)), # Yellow flowers
        (220, floor_y - 17, (150, 100, 200)), # Purple flowers
        (280, floor_y - 15, (255, 150, 150)), # Pink carnations
    ]

    for fx, fy, flower_color in flower_clusters:
        # Stems
        for i in range(5):
            sx = fx + i * 3
            pygame.draw.line(surface, (50, 100, 50), (sx, fy), (sx, fy + 15), 1)
            # Flower head
            pygame.draw.circle(surface, flower_color, (sx, fy - 2), 3)

    # === MEMORIAL PLAQUES ===
    plaque_data = [
        (w // 2 - 80, wall_y + 5, "IN MEMORY"),
        (w // 2 + 20, wall_y + 5, "FOREVER"),
    ]

    for plx, ply, text in plaque_data:
        pygame.draw.rect(surface, (150, 130, 100), (plx, ply, 55, 15))
        pygame.draw.rect(surface, (120, 100, 70), (plx + 2, ply + 2, 51, 11))
        try:
            font = pygame.font.Font(None, 10)
            plaque_text = font.render(text, True, (200, 180, 140))
            surface.blit(plaque_text, (plx + 5, ply + 4))
        except:
            pass

    # === NOTES AND MESSAGES ===
    # Post-it notes and cards left by visitors
    notes = [
        (60, 60, (255, 255, 150), "We miss you"),
        (190, 110, (255, 200, 200), "Thank you"),
        (270, 70, (200, 255, 200), "Legend"),
        (35, 115, (255, 220, 200), "Gone not forgotten"),
    ]

    for nx, ny, note_color, msg in notes:
        pygame.draw.rect(surface, note_color, (nx, ny, 22, 18))
        # Writing lines
        pygame.draw.line(surface, (100, 100, 120), (nx + 2, ny + 5), (nx + 20, ny + 5), 1)
        pygame.draw.line(surface, (100, 100, 120), (nx + 2, ny + 9), (nx + 18, ny + 9), 1)
        pygame.draw.line(surface, (100, 100, 120), (nx + 2, ny + 13), (nx + 20, ny + 13), 1)

    # === ATMOSPHERIC LIGHTING ===
    # Soft spotlights on the wall
    for lx in [80, 160, 240]:
        for i in range(3):
            alpha = 60 - i * 20
            pygame.draw.circle(surface, (255, 255, 230), (lx, 90), 25 + i * 15)

    # === ENTRANCE ===
    door_x = 0
    pygame.draw.rect(surface, (25, 25, 35), (door_x, floor_y - 75, 24, 75))

    return surface


def create_main_stage_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the legendary First Avenue main stage background - the climax location."""
    surface = pygame.Surface(size)
    w, h = size

    # Dramatic stage lighting gradient - deep purples to hot magentas
    create_gradient(surface, [
        (15, 5, 30),
        (60, 20, 100),
        (100, 40, 140),
        (50, 20, 80),
    ])

    # === STAGE FLOOR ===
    floor_y = h - 40
    pygame.draw.rect(surface, (25, 25, 30), (0, floor_y, w, 45))

    # Scuffed stage boards
    for i in range(0, w, 12):
        pygame.draw.line(surface, (30, 30, 35), (i, floor_y), (i, h), 1)

    # Stage wear marks
    for i in range(10):
        sx = random.randint(0, w)
        sy = random.randint(floor_y, h)
        pygame.draw.circle(surface, (20, 20, 25), (sx, sy), random.randint(2, 5))

    # === BACKDROP CURTAINS ===
    curtain_color = (80, 10, 40)
    curtain_highlight = (100, 20, 60)
    for i in range(0, w, 10):
        fold = i % 20 < 10
        color = curtain_highlight if fold else curtain_color
        pygame.draw.rect(surface, color, (i, 10, 10, floor_y - 10))
        # Curtain shading
        pygame.draw.line(surface, tuple(c - 20 for c in color), (i + 9, 10), (i + 9, floor_y - 10))

    # === DRUM KIT (center stage) ===
    drum_x = w // 2 - 30
    drum_y = floor_y - 45

    # Kick drum
    pygame.draw.ellipse(surface, (50, 50, 60), (drum_x + 15, drum_y + 25, 30, 20))
    pygame.draw.ellipse(surface, (40, 40, 50), (drum_x + 17, drum_y + 27, 26, 16))
    # Band logo on kick
    pygame.draw.circle(surface, (200, 180, 100), (drum_x + 30, drum_y + 35), 8)

    # Toms
    for i, tx in enumerate([drum_x, drum_x + 25, drum_x + 50]):
        pygame.draw.ellipse(surface, (60, 50, 70), (tx, drum_y + 10, 18, 12))
        pygame.draw.ellipse(surface, (50, 40, 60), (tx + 2, drum_y + 11, 14, 9))

    # Cymbals
    cymbal_positions = [(drum_x - 10, drum_y), (drum_x + 55, drum_y + 5), (drum_x + 30, drum_y - 5)]
    for cx, cy in cymbal_positions:
        pygame.draw.ellipse(surface, (180, 170, 100), (cx, cy, 20, 8))
        pygame.draw.ellipse(surface, (200, 190, 120), (cx + 2, cy + 1, 16, 5))
        # Cymbal stand
        pygame.draw.line(surface, (60, 60, 70), (cx + 10, cy + 8), (cx + 10, drum_y + 45), 2)

    # Drum stool
    pygame.draw.circle(surface, (50, 40, 45), (drum_x + 30, drum_y + 50), 8)
    pygame.draw.line(surface, (60, 50, 55), (drum_x + 30, drum_y + 58), (drum_x + 30, floor_y), 3)

    # === GUITAR AMPS (stage left) ===
    amp_x = 20
    for i in range(3):
        ay = floor_y - 60 + i * 18
        # Amp cabinet
        pygame.draw.rect(surface, (30, 30, 35), (amp_x, ay, 45, 16))
        pygame.draw.rect(surface, (40, 40, 45), (amp_x + 2, ay + 2, 41, 12))
        # Speaker grill
        for row in range(3):
            for col in range(8):
                pygame.draw.circle(surface, (25, 25, 30), (amp_x + 6 + col * 5, ay + 5 + row * 3), 1)
        # Control knobs
        for kx in range(4):
            pygame.draw.circle(surface, (200, 180, 100), (amp_x + 10 + kx * 8, ay + 2), 2)

    # === BASS AMP (stage right) ===
    bass_amp_x = w - 65
    pygame.draw.rect(surface, (35, 30, 40), (bass_amp_x, floor_y - 70, 55, 70))
    pygame.draw.rect(surface, (45, 40, 50), (bass_amp_x + 3, floor_y - 67, 49, 64))
    # Large speakers
    for i in range(2):
        speaker_y = floor_y - 62 + i * 32
        pygame.draw.circle(surface, (30, 30, 35), (bass_amp_x + 27, speaker_y), 12)
        pygame.draw.circle(surface, (40, 40, 45), (bass_amp_x + 27, speaker_y), 10)

    # === MICROPHONE STANDS ===
    mic_positions = [(w // 2, floor_y - 75), (120, floor_y - 65), (200, floor_y - 68)]
    for mx, my in mic_positions:
        # Stand
        pygame.draw.line(surface, (70, 70, 80), (mx, my + 75), (mx, my), 3)
        # Boom arm
        pygame.draw.line(surface, (70, 70, 80), (mx, my), (mx + 15, my - 8), 2)
        # Microphone
        pygame.draw.ellipse(surface, (90, 90, 100), (mx + 12, my - 12, 8, 12))
        pygame.draw.ellipse(surface, (60, 60, 70), (mx + 13, my - 11, 6, 10))

    # === STAGE MONITORS (floor wedges) ===
    monitor_positions = [(80, floor_y - 20), (160, floor_y - 15), (240, floor_y - 20)]
    for mon_x, mon_y in monitor_positions:
        # Wedge shape
        pygame.draw.polygon(surface, (35, 35, 40), [
            (mon_x, mon_y + 20),
            (mon_x + 30, mon_y + 20),
            (mon_x + 30, mon_y + 5),
            (mon_x + 5, mon_y),
        ])
        # Speaker grill
        pygame.draw.polygon(surface, (25, 25, 30), [
            (mon_x + 3, mon_y + 17),
            (mon_x + 27, mon_y + 17),
            (mon_x + 27, mon_y + 8),
            (mon_x + 8, mon_y + 3),
        ])

    # === SPOTLIGHT BEAMS ===
    spotlight_colors = [
        (255, 100, 200, 40),  # Magenta
        (100, 200, 255, 35),  # Cyan
        (255, 220, 100, 30),  # Gold
        (200, 100, 255, 38),  # Purple
    ]

    for i, (r, g, b, a) in enumerate(spotlight_colors):
        beam_x = 50 + i * 70
        # Create beam polygon
        beam_top = beam_x + random.randint(-10, 10)
        beam_spread = 40

        # Draw beam (using darker colors to simulate alpha on non-SRCALPHA surface)
        beam_color = (r // 3, g // 3, b // 3)
        pygame.draw.polygon(surface, beam_color, [
            (beam_top - 5, 0),
            (beam_top + 5, 0),
            (beam_x + beam_spread, floor_y - 30),
            (beam_x - beam_spread, floor_y - 30),
        ])

        # Bright center
        bright_color = (r // 2, g // 2, b // 2)
        pygame.draw.polygon(surface, bright_color, [
            (beam_top - 2, 0),
            (beam_top + 2, 0),
            (beam_x + beam_spread // 2, floor_y - 30),
            (beam_x - beam_spread // 2, floor_y - 30),
        ])

    # === CABLES ON STAGE FLOOR ===
    cable_colors = [(30, 30, 35), (35, 30, 30), (30, 35, 30)]
    for i, color in enumerate(cable_colors):
        start_x = 40 + i * 80
        cable_path = [
            (start_x, floor_y + 5),
            (start_x + 30, floor_y + 8),
            (start_x + 60, floor_y + 3),
            (start_x + 90, floor_y + 10),
        ]
        pygame.draw.lines(surface, color, False, cable_path, 3)

    # === ZOMBIE BAND MEMBERS (frozen mid-performance) ===
    # Guitarist (stage left)
    pygame.draw.ellipse(surface, (60, 80, 60), (90, floor_y - 55, 15, 25))  # Body
    pygame.draw.circle(surface, (70, 90, 70), (97, floor_y - 58), 7)  # Head
    # Guitar
    pygame.draw.ellipse(surface, (180, 50, 50), (85, floor_y - 45, 12, 20))
    pygame.draw.rect(surface, (80, 60, 40), (80, floor_y - 50, 15, 4))

    # Singer (center)
    pygame.draw.ellipse(surface, (80, 60, 80), (155, floor_y - 60, 18, 30))  # Body
    pygame.draw.circle(surface, (90, 70, 90), (164, floor_y - 63), 8)  # Head
    # Leather jacket detail
    pygame.draw.rect(surface, (60, 50, 60), (158, floor_y - 55, 12, 20))

    return surface


def create_back_alley_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create dark back alley behind First Avenue - shortcut location."""
    surface = pygame.Surface(size)
    w, h = size

    # Dark, moody gradient
    create_gradient(surface, [
        (10, 8, 15),
        (25, 20, 35),
        (35, 30, 45),
        (15, 12, 20),
    ])

    # === BRICK WALLS ===
    brick_color = (40, 30, 45)
    mortar_color = (30, 25, 35)
    brick_w, brick_h = 16, 8

    # Left wall
    for row in range(15):
        offset = (row % 2) * (brick_w // 2)
        for col in range(-1, 10):
            bx = col * brick_w + offset
            by = 10 + row * brick_h
            if bx < w // 2 - 40:  # Left side only
                pygame.draw.rect(surface, brick_color, (bx, by, brick_w - 1, brick_h - 1))

    # Right wall
    for row in range(15):
        offset = (row % 2) * (brick_w // 2)
        for col in range(10, 22):
            bx = col * brick_w + offset
            by = 10 + row * brick_h
            if bx > w // 2 + 40:  # Right side only
                pygame.draw.rect(surface, brick_color, (bx, by, brick_w - 1, brick_h - 1))

    # === GROUND / ASPHALT ===
    ground_y = h - 50
    pygame.draw.rect(surface, (30, 30, 35), (0, ground_y, w, 55))

    # Asphalt texture
    for i in range(50):
        gx = random.randint(0, w)
        gy = random.randint(ground_y, h)
        pygame.draw.circle(surface, (35, 35, 40), (gx, gy), 1)

    # === DUMPSTERS ===
    # Left dumpster
    dumpster_x = 20
    pygame.draw.rect(surface, (40, 60, 40), (dumpster_x, ground_y - 45, 55, 45))
    pygame.draw.rect(surface, (50, 70, 50), (dumpster_x, ground_y - 45, 55, 5))
    # Lid (slightly open)
    pygame.draw.polygon(surface, (35, 55, 35), [
        (dumpster_x, ground_y - 45),
        (dumpster_x + 55, ground_y - 50),
        (dumpster_x + 55, ground_y - 45),
        (dumpster_x, ground_y - 40),
    ])
    # Trash bags inside
    pygame.draw.circle(surface, (25, 25, 30), (dumpster_x + 20, ground_y - 25), 8)
    pygame.draw.circle(surface, (30, 30, 35), (dumpster_x + 35, ground_y - 20), 7)

    # Right dumpster
    dumpster_x2 = w - 75
    pygame.draw.rect(surface, (50, 50, 60), (dumpster_x2, ground_y - 40, 50, 40))
    pygame.draw.rect(surface, (60, 60, 70), (dumpster_x2, ground_y - 40, 50, 5))

    # === FIRE ESCAPE ===
    escape_x = 200
    # Ladder
    pygame.draw.rect(surface, (60, 55, 50), (escape_x, 40, 4, 100))
    pygame.draw.rect(surface, (60, 55, 50), (escape_x + 20, 40, 4, 100))
    # Rungs
    for i in range(10):
        rung_y = 45 + i * 10
        pygame.draw.rect(surface, (70, 65, 60), (escape_x, rung_y, 24, 3))

    # Platform above
    pygame.draw.rect(surface, (55, 50, 45), (escape_x - 10, 35, 45, 6))

    # === GRAFFITI ===
    graffiti_spots = [
        (30, 60, (255, 100, 200), "MPLS"),
        (w - 100, 50, (100, 200, 255), "82"),
        (120, 70, (255, 200, 100), "PUNK"),
    ]
    for gx, gy, color, text in graffiti_spots:
        # Spray paint effect
        try:
            font = pygame.font.Font(None, 24)
            graffiti = font.render(text, True, color)
            surface.blit(graffiti, (gx, gy))
            # Shadow/outline
            shadow = font.render(text, True, tuple(c // 3 for c in color))
            surface.blit(shadow, (gx + 2, gy + 2))
        except:
            pass

    # === STEAM VENTS ===
    vent_x = w // 2 - 30
    pygame.draw.rect(surface, (50, 50, 55), (vent_x, ground_y + 10, 20, 8))
    # Steam rising
    steam_color = (180, 180, 200)
    for i in range(5):
        steam_y = ground_y - i * 15
        steam_w = 15 + i * 3
        steam_alpha = 100 - i * 20
        # Simulate alpha with darker color
        steam_draw = tuple(c // (3 + i) for c in steam_color)
        pygame.draw.ellipse(surface, steam_draw, (vent_x - i * 2, steam_y, steam_w, 12))

    # === PUDDLES WITH NEON REFLECTIONS ===
    # Large puddle
    puddle_x = 110
    puddle_w = 60
    pygame.draw.ellipse(surface, (20, 20, 30), (puddle_x, ground_y + 15, puddle_w, 20))
    # Neon reflection (magenta glow from street)
    pygame.draw.ellipse(surface, (80, 20, 60), (puddle_x + 5, ground_y + 17, puddle_w - 10, 12))
    pygame.draw.ellipse(surface, (120, 40, 90), (puddle_x + 15, ground_y + 19, 30, 8))

    # === RATS ===
    rat_positions = [(45, ground_y + 8), (250, ground_y + 12)]
    for rx, ry in rat_positions:
        # Rat body
        pygame.draw.ellipse(surface, (40, 40, 45), (rx, ry, 12, 6))
        # Head
        pygame.draw.circle(surface, (45, 45, 50), (rx + 12, ry + 3), 3)
        # Tail
        tail_path = [(rx, ry + 3), (rx - 5, ry + 5), (rx - 8, ry + 2)]
        pygame.draw.lines(surface, (35, 35, 40), False, tail_path, 1)

    # === BACK DOOR TO VENUE ===
    door_x = w // 2 - 15
    pygame.draw.rect(surface, (50, 45, 55), (door_x, ground_y - 75, 30, 75))
    pygame.draw.rect(surface, (40, 35, 45), (door_x + 2, ground_y - 73, 26, 71))
    # Door handle
    pygame.draw.circle(surface, (150, 130, 100), (door_x + 24, ground_y - 40), 3)

    # Exit light above door
    pygame.draw.rect(surface, (255, 50, 50), (door_x + 5, ground_y - 85, 20, 8))
    # Glow
    for i in range(3):
        pygame.draw.rect(surface, (80, 20, 20),
                        (door_x + 5 - i, ground_y - 85 - i, 20 + i * 2, 8 + i * 2), 1)

    # === CARDBOARD BOXES ===
    box_x = 140
    pygame.draw.rect(surface, (60, 55, 50), (box_x, ground_y - 25, 25, 25))
    pygame.draw.rect(surface, (50, 45, 40), (box_x + 2, ground_y - 23, 21, 21))
    # Box tape
    pygame.draw.rect(surface, (120, 100, 80), (box_x + 8, ground_y - 25, 10, 25))

    # === DISTANT NEON GLOW ===
    # From main street (top of alley)
    for i in range(5):
        glow_y = 10 + i * 5
        glow_alpha = 60 - i * 10
        glow_color = (glow_alpha, glow_alpha // 3, glow_alpha // 2)
        pygame.draw.rect(surface, glow_color, (0, glow_y, w, 3))

    return surface


def create_venue_basement_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create creepy storage basement under First Avenue."""
    surface = pygame.Surface(size)
    w, h = size

    # Dark, oppressive gradient
    create_gradient(surface, [
        (15, 12, 20),
        (25, 20, 30),
        (20, 15, 25),
        (12, 10, 15),
    ])

    # === CONCRETE FLOOR ===
    floor_y = h - 45
    pygame.draw.rect(surface, (40, 40, 45), (0, floor_y, w, 50))

    # Floor stains and cracks
    pygame.draw.line(surface, (30, 30, 35), (20, floor_y + 5), (80, h), 2)
    pygame.draw.line(surface, (30, 30, 35), (200, floor_y + 10), (250, h), 1)
    # Water stain
    pygame.draw.ellipse(surface, (35, 35, 40), (100, floor_y + 15, 50, 20))

    # === CINDERBLOCK WALLS ===
    block_color = (45, 45, 50)
    block_shadow = (35, 35, 40)
    block_w, block_h = 20, 10

    for row in range(12):
        offset = (row % 2) * (block_w // 2)
        for col in range(-1, w // block_w + 2):
            bx = col * block_w + offset
            by = 15 + row * block_h
            if by < floor_y:
                pygame.draw.rect(surface, block_color, (bx, by, block_w - 1, block_h - 1))
                pygame.draw.rect(surface, block_shadow, (bx, by + block_h - 2, block_w - 1, 2))

    # === EXPOSED PIPES (CEILING) ===
    pipe_y = 25
    # Horizontal pipes
    pygame.draw.rect(surface, (80, 75, 70), (0, pipe_y, w, 6))
    pygame.draw.rect(surface, (90, 85, 80), (0, pipe_y, w, 2))

    pygame.draw.rect(surface, (70, 65, 60), (0, pipe_y + 15, w, 5))
    pygame.draw.rect(surface, (80, 75, 70), (0, pipe_y + 15, w, 2))

    # Pipe joints
    for px in range(0, w, 60):
        pygame.draw.rect(surface, (60, 55, 50), (px, pipe_y - 2, 8, 10))

    # === SINGLE FLICKERING BULB ===
    bulb_x, bulb_y = w // 2, 35
    # Cord
    pygame.draw.line(surface, (40, 40, 45), (bulb_x, 10), (bulb_x, bulb_y), 2)
    # Socket
    pygame.draw.rect(surface, (50, 50, 55), (bulb_x - 4, bulb_y, 8, 8))
    # Bulb
    pygame.draw.circle(surface, (255, 240, 200), (bulb_x, bulb_y + 12), 6)
    pygame.draw.circle(surface, (200, 180, 150), (bulb_x, bulb_y + 12), 4)

    # Light glow (flickering effect)
    for i in range(5):
        alpha = 150 - i * 30
        glow_color = (alpha // 2, alpha // 2, alpha // 3)
        pygame.draw.circle(surface, glow_color, (bulb_x, bulb_y + 12), 15 + i * 8)

    # === STORAGE CRATES ===
    crate_positions = [
        (20, floor_y - 50, 45, 50),
        (70, floor_y - 40, 40, 40),
        (w - 90, floor_y - 55, 50, 55),
        (w - 130, floor_y - 35, 35, 35),
    ]

    for cx, cy, cw, ch in crate_positions:
        # Crate body
        pygame.draw.rect(surface, (50, 45, 40), (cx, cy, cw, ch))
        pygame.draw.rect(surface, (60, 55, 50), (cx, cy, cw, 3))
        # Wood slats
        for i in range(3):
            slat_y = cy + 5 + i * (ch // 4)
            pygame.draw.line(surface, (40, 35, 30), (cx, slat_y), (cx + cw, slat_y), 2)
        # Stenciled text
        pygame.draw.rect(surface, (30, 30, 35), (cx + 5, cy + ch // 2 - 5, cw - 10, 10))

    # === OLD BAND EQUIPMENT ===
    # Guitar amp stack
    amp_x = 130
    for i in range(3):
        ay = floor_y - 60 + i * 18
        pygame.draw.rect(surface, (35, 30, 35), (amp_x, ay, 50, 16))
        pygame.draw.rect(surface, (45, 40, 45), (amp_x + 2, ay + 2, 46, 12))
        # Speaker grill
        for row in range(2):
            for col in range(9):
                pygame.draw.circle(surface, (30, 25, 30), (amp_x + 5 + col * 5, ay + 5 + row * 4), 1)

    # Drum cases
    case_x = 200
    pygame.draw.ellipse(surface, (40, 35, 40), (case_x, floor_y - 30, 30, 30))
    pygame.draw.ellipse(surface, (50, 45, 50), (case_x + 2, floor_y - 28, 26, 26))

    # Microphone stand (broken)
    pygame.draw.line(surface, (60, 60, 65), (250, floor_y - 5), (260, floor_y - 45), 3)

    # === COBWEBS ===
    web_points = [
        [(10, 40), (30, 45), (25, 55), (15, 50)],
        [(w - 30, 50), (w - 15, 55), (w - 20, 65), (w - 35, 60)],
        [(bulb_x - 20, bulb_y + 5), (bulb_x - 10, bulb_y + 15), (bulb_x - 15, bulb_y + 20)],
    ]

    for web in web_points:
        pygame.draw.lines(surface, (180, 180, 190), False, web, 1)
        # Add connecting threads
        for i in range(len(web) - 1):
            pygame.draw.line(surface, (180, 180, 190), web[i], web[i + 1], 1)

    # === HIDDEN MEMORABILIA ===
    # Old posters (rolled up)
    pygame.draw.rect(surface, (200, 180, 150), (50, floor_y - 15, 6, 25))
    pygame.draw.rect(surface, (180, 160, 130), (57, floor_y - 15, 6, 25))

    # Vintage records leaning against wall
    for i in range(4):
        rec_x = w - 50 + i * 3
        pygame.draw.rect(surface, (30, 30, 35), (rec_x, floor_y - 25, 3, 25))

    # === MYSTERIOUS SHADOW IN CORNER ===
    shadow_x = 5
    pygame.draw.ellipse(surface, (8, 8, 12), (shadow_x, floor_y - 40, 25, 40))

    # === STAIRS (partial view) ===
    stairs_x = w - 45
    for i in range(4):
        step_y = floor_y - 10 - i * 8
        pygame.draw.rect(surface, (50, 48, 52), (stairs_x, step_y, 40, 8))
        pygame.draw.rect(surface, (45, 43, 47), (stairs_x, step_y + 6, 40, 2))

    return surface


def create_tour_bus_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create intimate tour bus interior - character moment location."""
    surface = pygame.Surface(size)
    w, h = size

    # Warm interior lighting gradient
    create_gradient(surface, [
        (40, 35, 30),
        (60, 50, 45),
        (70, 60, 55),
        (50, 45, 40),
    ])

    # === BUS FLOOR ===
    floor_y = h - 35
    pygame.draw.rect(surface, (55, 50, 45), (0, floor_y, w, 40))

    # Floor pattern (rubber matting)
    for i in range(0, w, 8):
        pygame.draw.line(surface, (50, 45, 40), (i, floor_y), (i, h), 1)

    # === BUS WALLS (CURVED) ===
    wall_color = (65, 60, 70)
    # Left wall
    pygame.draw.rect(surface, wall_color, (0, 30, 15, floor_y - 30))
    # Curve at top
    pygame.draw.arc(surface, wall_color, (-20, 10, 60, 40), 0, 3.14, 3)

    # Right wall
    pygame.draw.rect(surface, wall_color, (w - 15, 30, 15, floor_y - 30))

    # === BUNKS (stacked) ===
    bunk_x = 20
    bunk_w = 80

    # Lower bunk
    pygame.draw.rect(surface, (60, 50, 45), (bunk_x, floor_y - 40, bunk_w, 40))
    pygame.draw.rect(surface, (80, 70, 60), (bunk_x + 2, floor_y - 38, bunk_w - 4, 36))
    # Mattress
    pygame.draw.rect(surface, (90, 80, 70), (bunk_x + 5, floor_y - 35, bunk_w - 10, 8))
    # Pillow
    pygame.draw.rect(surface, (200, 190, 180), (bunk_x + 8, floor_y - 35, 18, 8))
    # Blanket (rumpled)
    pygame.draw.rect(surface, (70, 90, 110), (bunk_x + 30, floor_y - 32, 45, 15))

    # Upper bunk
    pygame.draw.rect(surface, (55, 45, 40), (bunk_x, floor_y - 85, bunk_w, 40))
    pygame.draw.rect(surface, (75, 65, 55), (bunk_x + 2, floor_y - 83, bunk_w - 4, 36))
    # Curtain (partially closed)
    pygame.draw.rect(surface, (50, 70, 90), (bunk_x + 50, floor_y - 83, 40, 38))

    # Bunk ladder
    pygame.draw.rect(surface, (70, 60, 55), (bunk_x + bunk_w - 5, floor_y - 85, 3, 85))
    for i in range(5):
        rung_y = floor_y - 75 + i * 18
        pygame.draw.rect(surface, (80, 70, 65), (bunk_x + bunk_w - 15, rung_y, 15, 3))

    # === EQUIPMENT CASES ===
    case_positions = [
        (bunk_x + bunk_w + 20, floor_y - 60, 45, 60),
        (bunk_x + bunk_w + 70, floor_y - 50, 40, 50),
    ]

    for cx, cy, cw, ch in case_positions:
        # Case body
        pygame.draw.rect(surface, (30, 30, 35), (cx, cy, cw, ch))
        pygame.draw.rect(surface, (50, 50, 55), (cx + 1, cy + 1, cw - 2, ch - 2))
        # Corners
        corner_size = 6
        for corner_x in [cx, cx + cw - corner_size]:
            for corner_y in [cy, cy + ch - corner_size]:
                pygame.draw.rect(surface, (150, 140, 100), (corner_x, corner_y, corner_size, corner_size))
        # Latches
        pygame.draw.rect(surface, (180, 170, 120), (cx + cw // 2 - 8, cy + ch - 10, 16, 5))

    # === ROAD MAPS ON WALL ===
    map_x, map_y = 115, 35
    pygame.draw.rect(surface, (200, 190, 170), (map_x, map_y, 50, 40))
    pygame.draw.rect(surface, (220, 210, 190), (map_x + 2, map_y + 2, 46, 36))
    # Map lines (roads)
    road_colors = [(200, 50, 50), (50, 50, 200), (50, 200, 50)]
    for i, color in enumerate(road_colors):
        start_x = map_x + 5 + i * 10
        start_y = map_y + 5
        pygame.draw.line(surface, color, (start_x, start_y), (start_x + 20, start_y + 30), 2)

    # === BAND POSTERS (1982) ===
    poster_data = [
        (175, 40, (255, 180, 80), "PRINCE\n82 TOUR"),
        (230, 45, (200, 100, 200), "HUSKER\nDU"),
        (270, 38, (100, 200, 255), "MPLS\nSCENE"),
    ]

    for px, py, color, text in poster_data:
        pygame.draw.rect(surface, color, (px, py, 35, 45))
        pygame.draw.rect(surface, (30, 30, 40), (px, py, 35, 45), 1)
        # Poster image area
        pygame.draw.rect(surface, tuple(c - 50 for c in color), (px + 3, py + 3, 29, 25))

    # === OVERHEAD STORAGE ===
    storage_y = 20
    pygame.draw.rect(surface, (60, 55, 65), (100, storage_y, 150, 15))
    pygame.draw.rect(surface, (70, 65, 75), (100, storage_y, 150, 3))
    # Items visible
    pygame.draw.circle(surface, (200, 200, 210), (120, storage_y + 7), 5)  # Hat
    pygame.draw.rect(surface, (180, 100, 50), (140, storage_y + 4, 8, 8))  # Box

    # === SMALL TABLE ===
    table_x = w - 80
    table_y = floor_y - 35
    pygame.draw.rect(surface, (70, 60, 55), (table_x, table_y, 60, 35))
    pygame.draw.rect(surface, (80, 70, 65), (table_x, table_y, 60, 3))

    # Coffee cups on table
    pygame.draw.ellipse(surface, (200, 200, 200), (table_x + 10, table_y - 8, 12, 8))
    pygame.draw.ellipse(surface, (180, 160, 140), (table_x + 35, table_y - 8, 12, 8))

    # Playing cards
    for i in range(3):
        card_x = table_x + 15 + i * 8
        pygame.draw.rect(surface, (240, 240, 250), (card_x, table_y + 8, 12, 16))
        pygame.draw.rect(surface, (200, 50, 50), (card_x + 2, table_y + 10, 8, 3))

    # === WINDOW ===
    window_x = w - 55
    window_y = 50
    pygame.draw.rect(surface, (80, 75, 85), (window_x, window_y, 45, 35))
    # Night view with stars
    pygame.draw.rect(surface, (15, 10, 25), (window_x + 3, window_y + 3, 39, 29))
    # Stars
    for _ in range(8):
        star_x = window_x + 5 + random.randint(0, 35)
        star_y = window_y + 5 + random.randint(0, 25)
        surface.set_at((star_x, star_y), (200, 200, 220))
    # Window frame
    pygame.draw.rect(surface, (90, 85, 95), (window_x, window_y, 45, 35), 2)

    # === GUITAR CASE (leaning) ===
    guitar_x = 15
    pygame.draw.polygon(surface, (40, 35, 30), [
        (guitar_x, floor_y - 10),
        (guitar_x + 25, floor_y - 10),
        (guitar_x + 30, floor_y - 70),
        (guitar_x + 5, floor_y - 70),
    ])
    # Case details
    pygame.draw.line(surface, (120, 100, 80), (guitar_x + 8, floor_y - 40), (guitar_x + 22, floor_y - 40), 1)

    # === OVERHEAD LIGHT ===
    light_x = w // 2
    light_y = 22
    pygame.draw.rect(surface, (200, 180, 150), (light_x - 15, light_y, 30, 8))
    # Glow
    for i in range(4):
        glow_alpha = 100 - i * 25
        glow_color = (glow_alpha, glow_alpha - 10, glow_alpha - 20)
        pygame.draw.ellipse(surface, glow_color, (light_x - 25 - i * 5, light_y + 8, 50 + i * 10, 20 + i * 5))

    return surface


def create_rooftop_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create rooftop of First Avenue - reflective ending location."""
    surface = pygame.Surface(size)
    w, h = size

    # Night sky gradient with stars
    create_gradient(surface, [
        (5, 5, 15),
        (15, 10, 30),
        (25, 15, 45),
        (35, 20, 55),
    ])

    # === STARS AND MOON ===
    draw_stars(surface, 80)

    # Moon
    moon_x, moon_y = 250, 40
    pygame.draw.circle(surface, (240, 235, 220), (moon_x, moon_y), 18)
    pygame.draw.circle(surface, (220, 215, 200), (moon_x, moon_y), 16)
    # Moon craters
    pygame.draw.circle(surface, (200, 195, 180), (moon_x - 5, moon_y - 3), 4)
    pygame.draw.circle(surface, (210, 205, 190), (moon_x + 6, moon_y + 4), 3)

    # === DISTANT MINNEAPOLIS SKYLINE ===
    skyline_y = h - 100
    skyline_buildings = [
        (0, 60, 40),
        (45, 75, 50),
        (100, 85, 45),
        (150, 70, 55),
        (210, 80, 40),
        (255, 65, 50),
    ]

    for bx, bh, bw in skyline_buildings:
        by = skyline_y - bh
        # Building silhouette
        pygame.draw.rect(surface, (25, 20, 35), (bx, by, bw, bh))
        pygame.draw.rect(surface, (30, 25, 40), (bx, by, bw, 2))

        # Lit windows
        window_color = (255, 230, 150)
        dark_window = (40, 35, 50)

        win_cols = max(1, bw // 12)
        win_rows = max(1, bh // 12)

        for row in range(win_rows):
            for col in range(win_cols):
                wx = bx + 5 + col * 10
                wy = by + 8 + row * 10

                if random.random() > 0.4:
                    pygame.draw.rect(surface, window_color, (wx, wy, 5, 6))
                else:
                    pygame.draw.rect(surface, dark_window, (wx, wy, 5, 6))

    # === ROOFTOP SURFACE ===
    roof_y = h - 45
    pygame.draw.rect(surface, (40, 40, 45), (0, roof_y, w, 50))

    # Tar paper texture
    for i in range(30):
        tx = random.randint(0, w)
        ty = random.randint(roof_y, h)
        pygame.draw.circle(surface, (45, 45, 50), (tx, ty), 2)

    # Roof gravel
    for i in range(50):
        gx = random.randint(0, w)
        gy = random.randint(roof_y, h)
        pygame.draw.circle(surface, (50, 50, 55), (gx, gy), 1)

    # === WATER TOWER (iconic) ===
    tower_x = 200
    tower_base_y = roof_y - 30

    # Support legs
    pygame.draw.line(surface, (60, 60, 70), (tower_x - 15, tower_base_y), (tower_x - 10, roof_y), 3)
    pygame.draw.line(surface, (60, 60, 70), (tower_x + 15, tower_base_y), (tower_x + 10, roof_y), 3)

    # Tank
    pygame.draw.ellipse(surface, (70, 70, 80), (tower_x - 25, tower_base_y - 30, 50, 20))
    pygame.draw.rect(surface, (65, 65, 75), (tower_x - 25, tower_base_y - 30, 50, 15))
    pygame.draw.ellipse(surface, (60, 60, 70), (tower_x - 25, tower_base_y - 45, 50, 20))

    # Tower detail
    pygame.draw.rect(surface, (55, 55, 65), (tower_x - 22, tower_base_y - 40, 44, 25))

    # === VENTILATION UNITS ===
    vent_positions = [(40, roof_y - 25, 30, 25), (90, roof_y - 20, 25, 20)]

    for vx, vy, vw, vh in vent_positions:
        pygame.draw.rect(surface, (50, 50, 55), (vx, vy, vw, vh))
        pygame.draw.rect(surface, (60, 60, 65), (vx, vy, vw, 3))
        # Grillwork
        for i in range(3):
            grill_y = vy + 6 + i * 6
            pygame.draw.line(surface, (40, 40, 45), (vx + 2, grill_y), (vx + vw - 2, grill_y), 1)

    # === NEON SIGNS VISIBLE BELOW ===
    # Glow from street level rising up
    neon_glow_positions = [
        (50, h - 60, (255, 100, 200)),
        (150, h - 70, (100, 200, 255)),
        (w - 80, h - 65, (255, 200, 100)),
    ]

    for nx, ny, (r, g, b) in neon_glow_positions:
        # Simulate neon glow from below
        for i in range(5):
            alpha = 80 - i * 15
            glow_color = (r // (3 + i), g // (3 + i), b // (3 + i))
            pygame.draw.ellipse(surface, glow_color, (nx - i * 3, ny - i * 2, 20 + i * 6, 10 + i * 3))

    # === ROOFTOP ACCESS DOOR ===
    door_x = 15
    door_y = roof_y - 70
    pygame.draw.rect(surface, (55, 50, 60), (door_x, door_y, 35, 70))
    pygame.draw.rect(surface, (45, 40, 50), (door_x + 2, door_y + 2, 31, 66))
    # Door window
    pygame.draw.rect(surface, (30, 30, 40), (door_x + 8, door_y + 8, 19, 25))
    # Light from inside
    pygame.draw.rect(surface, (100, 90, 70), (door_x + 10, door_y + 10, 15, 21))

    # === ANTENNA ===
    antenna_x = w - 40
    antenna_base_y = roof_y - 15

    # Main pole
    pygame.draw.rect(surface, (70, 70, 75), (antenna_x, roof_y - 90, 3, 90))

    # Cross bars
    pygame.draw.line(surface, (65, 65, 70), (antenna_x - 12, roof_y - 70), (antenna_x + 15, roof_y - 70), 2)
    pygame.draw.line(surface, (65, 65, 70), (antenna_x - 8, roof_y - 50), (antenna_x + 11, roof_y - 50), 2)

    # Red light on top
    pygame.draw.circle(surface, (255, 50, 50), (antenna_x + 1, roof_y - 92), 3)
    # Light glow
    for i in range(3):
        pygame.draw.circle(surface, (80, 20, 20), (antenna_x + 1, roof_y - 92), 5 + i * 2)

    # === GRAFFITI ON LEDGE ===
    ledge_x = 120
    ledge_y = roof_y - 5
    try:
        font = pygame.font.Font(None, 16)
        graffiti = font.render("MPLS FOREVER", True, (200, 100, 255))
        surface.blit(graffiti, (ledge_x, ledge_y))
    except:
        pass

    # === PIGEON ===
    pigeon_x, pigeon_y = 180, roof_y - 8
    pygame.draw.ellipse(surface, (60, 60, 70), (pigeon_x, pigeon_y, 12, 8))
    pygame.draw.circle(surface, (65, 65, 75), (pigeon_x + 10, pigeon_y + 2), 4)

    return surface




def create_practice_space_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the dingy warehouse practice space background."""
    surface = pygame.Surface(size)
    w, h = size

    # Dim warehouse gradient
    create_gradient(surface, [
        (35, 30, 40),
        (55, 50, 65),
        (40, 35, 50),
    ])

    # Concrete floor
    floor_y = h - 50
    pygame.draw.rect(surface, (55, 55, 60), (0, floor_y, w, 55))
    # Oil stains
    pygame.draw.ellipse(surface, (40, 40, 45), (80, floor_y + 10, 30, 15))
    pygame.draw.ellipse(surface, (45, 40, 45), (200, floor_y + 20, 25, 12))

    # === EGG CRATE FOAM WALLS ===
    # Left wall
    foam_color = (60, 55, 70)
    for row in range(8):
        for col in range(3):
            fx = 10 + col * 16
            fy = 25 + row * 18
            # Egg crate pattern
            pygame.draw.rect(surface, foam_color, (fx, fy, 14, 16))
            pygame.draw.polygon(surface, (50, 45, 60), [
                (fx + 2, fy + 2), (fx + 7, fy + 8), (fx + 2, fy + 14)
            ])
            pygame.draw.polygon(surface, (50, 45, 60), [
                (fx + 12, fy + 2), (fx + 7, fy + 8), (fx + 12, fy + 14)
            ])

    # Right wall
    for row in range(8):
        for col in range(3):
            fx = w - 58 + col * 16
            fy = 25 + row * 18
            pygame.draw.rect(surface, foam_color, (fx, fy, 14, 16))
            pygame.draw.polygon(surface, (50, 45, 60), [
                (fx + 2, fy + 2), (fx + 7, fy + 8), (fx + 2, fy + 14)
            ])
            pygame.draw.polygon(surface, (50, 45, 60), [
                (fx + 12, fy + 2), (fx + 7, fy + 8), (fx + 12, fy + 14)
            ])

    # === DRUM KIT ===
    drum_x = 70
    # Kick drum
    pygame.draw.ellipse(surface, (120, 30, 30), (drum_x, floor_y - 35, 40, 35))
    pygame.draw.ellipse(surface, (150, 50, 50), (drum_x + 5, floor_y - 30, 30, 25))
    # Bass drum logo
    pygame.draw.circle(surface, (255, 255, 255), (drum_x + 20, floor_y - 17), 8)

    # Snare drum
    pygame.draw.ellipse(surface, (180, 180, 190), (drum_x + 25, floor_y - 55, 20, 12))
    pygame.draw.ellipse(surface, (160, 160, 170), (drum_x + 27, floor_y - 54, 16, 10))

    # Tom-toms
    pygame.draw.ellipse(surface, (140, 80, 40), (drum_x - 10, floor_y - 60, 18, 14))
    pygame.draw.ellipse(surface, (140, 80, 40), (drum_x + 45, floor_y - 58, 18, 14))

    # Hi-hat stand
    pygame.draw.line(surface, (150, 150, 160), (drum_x - 15, floor_y - 70), (drum_x - 15, floor_y), 2)
    pygame.draw.ellipse(surface, (200, 180, 100), (drum_x - 22, floor_y - 75, 14, 6))
    pygame.draw.ellipse(surface, (200, 180, 100), (drum_x - 22, floor_y - 82, 14, 6))

    # Cymbal stands
    for cx in [drum_x - 25, drum_x + 60]:
        pygame.draw.line(surface, (140, 140, 150), (cx, floor_y - 85), (cx, floor_y), 2)
        pygame.draw.ellipse(surface, (220, 200, 120), (cx - 12, floor_y - 90, 24, 8))

    # === GUITAR AMPS ===
    amp_x = 200
    # Marshall stack
    for i in range(2):
        ay = floor_y - 80 + i * 40
        pygame.draw.rect(surface, (30, 30, 35), (amp_x, ay, 50, 38))
        pygame.draw.rect(surface, (200, 180, 100), (amp_x + 2, ay + 2, 46, 6))
        # Speaker grill
        pygame.draw.rect(surface, (50, 45, 50), (amp_x + 5, ay + 12, 40, 22))
        for gx in range(4):
            for gy in range(2):
                pygame.draw.circle(surface, (70, 65, 70),
                                 (amp_x + 12 + gx * 10, ay + 18 + gy * 8), 3)
        # Control knobs
        for k in range(6):
            pygame.draw.circle(surface, (180, 160, 100), (amp_x + 8 + k * 7, ay + 37), 2)

    # === BASS AMP ===
    bass_x = 170
    pygame.draw.rect(surface, (35, 35, 40), (bass_x, floor_y - 55, 45, 55))
    pygame.draw.rect(surface, (60, 55, 60), (bass_x + 5, floor_y - 50, 35, 45))
    # Large speaker cone
    pygame.draw.circle(surface, (40, 40, 45), (bass_x + 22, floor_y - 28), 15)
    pygame.draw.circle(surface, (80, 75, 80), (bass_x + 22, floor_y - 28), 10)

    # === BEAT-UP COUCH ===
    couch_x = w - 90
    pygame.draw.rect(surface, (80, 60, 50), (couch_x, floor_y - 35, 70, 35))
    pygame.draw.rect(surface, (70, 50, 40), (couch_x + 5, floor_y - 30, 60, 25))
    # Cushion tears
    pygame.draw.line(surface, (50, 40, 30), (couch_x + 20, floor_y - 25), (couch_x + 30, floor_y - 15), 2)
    # Stuffing
    pygame.draw.circle(surface, (220, 220, 230), (couch_x + 25, floor_y - 20), 3)

    # === ASHTRAYS ===
    for ax in [couch_x + 15, 125, 190]:
        pygame.draw.ellipse(surface, (60, 60, 65), (ax, floor_y - 3, 10, 6))
        # Cigarette butts
        pygame.draw.rect(surface, (220, 220, 200), (ax + 3, floor_y - 4, 3, 2))

    # === COFFEE CUPS ===
    # On floor
    pygame.draw.ellipse(surface, (140, 100, 80), (140, floor_y - 8, 8, 10))
    pygame.draw.ellipse(surface, (100, 70, 50), (142, floor_y - 6, 4, 6))

    # On amp
    pygame.draw.ellipse(surface, (200, 200, 210), (amp_x + 35, floor_y - 82, 8, 5))

    # === MICROPHONE STANDS ===
    for mx in [120, 160]:
        # Stand base
        pygame.draw.ellipse(surface, (60, 60, 70), (mx - 8, floor_y - 5, 16, 8))
        # Pole
        pygame.draw.line(surface, (70, 70, 80), (mx, floor_y - 5), (mx, floor_y - 100), 3)
        # Boom arm
        pygame.draw.line(surface, (70, 70, 80), (mx, floor_y - 100), (mx + 25, floor_y - 95), 2)
        # Microphone
        pygame.draw.circle(surface, (50, 50, 55), (mx + 25, floor_y - 95), 5)
        pygame.draw.circle(surface, (80, 80, 90), (mx + 25, floor_y - 95), 3)

    # === CABLES EVERYWHERE ===
    cable_paths = [
        [(drum_x + 20, floor_y - 15), (drum_x + 40, floor_y - 10), (amp_x - 10, floor_y - 5)],
        [(bass_x, floor_y - 25), (bass_x + 30, floor_y - 18), (bass_x + 50, floor_y - 3)],
        [(120, floor_y - 90), (140, floor_y - 50), (160, floor_y - 15)],
    ]
    for path in cable_paths:
        pygame.draw.lines(surface, (30, 30, 35), False, path, 3)

    # === SETLIST TAPED TO WALL ===
    pygame.draw.rect(surface, (240, 235, 220), (65, 35, 25, 30))
    pygame.draw.rect(surface, (30, 30, 35), (65, 35, 25, 30), 1)
    # Tape
    pygame.draw.rect(surface, (220, 210, 180), (72, 33, 11, 4))
    # Handwritten lines
    for i in range(6):
        pygame.draw.line(surface, (50, 50, 60), (68, 40 + i * 4), (87, 40 + i * 4), 1)

    # === HANGING LIGHT BULB ===
    # Wire
    pygame.draw.line(surface, (80, 80, 90), (w // 2, 10), (w // 2, 60), 1)
    # Bulb
    pygame.draw.ellipse(surface, (255, 240, 180), (w // 2 - 8, 60, 16, 22))
    # Glow
    for i in range(5):
        alpha = 150 - i * 30
        pygame.draw.circle(surface, (255, 240, 200), (w // 2, 71), 15 + i * 5)

    # === DOOR ===
    pygame.draw.rect(surface, (60, 55, 65), (0, floor_y - 80, 28, 80))
    pygame.draw.rect(surface, (50, 45, 55), (2, floor_y - 78, 24, 76))
    pygame.draw.circle(surface, (150, 140, 120), (23, floor_y - 40), 3)

    return surface


def create_club_bathroom_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the grungy club bathroom background."""
    surface = pygame.Surface(size)
    w, h = size

    # Sickly fluorescent gradient
    create_gradient(surface, [
        (80, 90, 85),
        (110, 125, 115),
        (70, 80, 75),
    ])

    # Grimy tile floor
    floor_y = h - 55
    tile_color = (85, 95, 90)
    tile_grout = (60, 70, 65)

    for row in range(6):
        for col in range(16):
            tx = col * 20
            ty = floor_y + row * 10
            pygame.draw.rect(surface, tile_color, (tx, ty, 19, 9))
            pygame.draw.rect(surface, tile_grout, (tx, ty, 19, 9), 1)

    # === WALL TILES ===
    wall_tile = (95, 105, 100)
    for row in range(12):
        for col in range(16):
            wx = col * 20
            wy = 20 + row * 12
            pygame.draw.rect(surface, wall_tile, (wx, wy, 19, 11))
            pygame.draw.rect(surface, tile_grout, (wx, wy, 19, 11), 1)
            # Water stains
            if random.random() > 0.85:
                stain = (75, 80, 75)
                pygame.draw.circle(surface, stain, (wx + 10, wy + 6), random.randint(3, 6))

    # === BATHROOM STALLS ===
    stall_x = 180
    # Stall divider
    pygame.draw.rect(surface, (65, 70, 75), (stall_x, floor_y - 100, 4, 100))

    # Stall doors
    for i in range(2):
        door_x = stall_x + 10 + i * 60
        pygame.draw.rect(surface, (70, 75, 80), (door_x, floor_y - 90, 50, 80))
        pygame.draw.rect(surface, (60, 65, 70), (door_x + 2, floor_y - 88, 46, 76))
        # Gap at bottom
        pygame.draw.rect(surface, tile_color, (door_x, floor_y - 15, 50, 15))
        # Door hinge
        pygame.draw.rect(surface, (100, 100, 110), (door_x + 2, floor_y - 70, 3, 8))
        pygame.draw.rect(surface, (100, 100, 110), (door_x + 2, floor_y - 40, 3, 8))
        # Lock indicator
        lock_color = (255, 50, 50) if i == 0 else (50, 255, 50)
        pygame.draw.circle(surface, lock_color, (door_x + 25, floor_y - 50), 4)

    # === GRAFFITI ON STALLS ===
    graffiti_items = [
        (door_x - 50, floor_y - 65, "MAYA WAS HERE", (255, 100, 150)),
        (door_x - 48, floor_y - 45, "PUNK'S NOT DEAD", (100, 255, 100)),
        (door_x + 15, floor_y - 75, "MPLS 82", (255, 200, 100)),
    ]

    for gx, gy, text, color in graffiti_items:
        try:
            font = pygame.font.Font(None, 14)
            graffiti = font.render(text, True, color)
            surface.blit(graffiti, (gx, gy))
            # Drip effect
            pygame.draw.line(surface, color, (gx + len(text) * 3, gy + 12),
                           (gx + len(text) * 3, gy + 18), 1)
        except:
            pass

    # === SINK ===
    sink_x = 40
    # Sink basin
    pygame.draw.rect(surface, (200, 200, 210), (sink_x, floor_y - 35, 55, 8))
    pygame.draw.ellipse(surface, (180, 180, 190), (sink_x + 5, floor_y - 33, 45, 6))
    pygame.draw.ellipse(surface, (140, 140, 150), (sink_x + 15, floor_y - 31, 25, 4))

    # Faucet
    pygame.draw.rect(surface, (160, 160, 170), (sink_x + 25, floor_y - 50, 5, 15))
    pygame.draw.arc(surface, (160, 160, 170), (sink_x + 15, floor_y - 55, 25, 10),
                   0, math.pi, 3)

    # Rust stains
    pygame.draw.line(surface, (140, 90, 60), (sink_x + 27, floor_y - 35),
                    (sink_x + 27, floor_y - 28), 2)

    # === CRACKED MIRROR ===
    mirror_x = 35
    mirror_w = 65
    mirror_h = 50
    mirror_y = floor_y - 95

    # Mirror frame
    pygame.draw.rect(surface, (80, 80, 90), (mirror_x, mirror_y, mirror_w, mirror_h))
    # Mirror surface
    pygame.draw.rect(surface, (150, 160, 165), (mirror_x + 3, mirror_y + 3, mirror_w - 6, mirror_h - 6))

    # Crack pattern
    crack_points = [
        (mirror_x + 45, mirror_y + 15),
        (mirror_x + 55, mirror_y + 25),
        (mirror_x + 50, mirror_y + 40),
    ]
    pygame.draw.lines(surface, (100, 110, 115), False, crack_points, 2)

    # Another crack
    pygame.draw.line(surface, (100, 110, 115), (mirror_x + 20, mirror_y + 10),
                    (mirror_x + 35, mirror_y + 35), 2)

    # === FLICKERING FLUORESCENT LIGHTS ===
    for lx in [80, 160, 240]:
        # Light fixture
        pygame.draw.rect(surface, (200, 200, 210), (lx, 15, 40, 8))
        pygame.draw.rect(surface, (220, 220, 230), (lx + 2, 17, 36, 4))
        # Flicker glow (uneven)
        brightness = random.choice([180, 200, 230, 255])
        for i in range(3):
            pygame.draw.rect(surface, (brightness, brightness, 230),
                           (lx - i * 5, 23, 40 + i * 10, 15 + i * 3), 1)

    # === PAPER TOWEL DISPENSER ===
    dispenser_x = 115
    pygame.draw.rect(surface, (150, 150, 160), (dispenser_x, floor_y - 75, 30, 35))
    pygame.draw.rect(surface, (130, 130, 140), (dispenser_x + 3, floor_y - 72, 24, 29))
    # Paper hanging out
    pygame.draw.rect(surface, (240, 235, 230), (dispenser_x + 10, floor_y - 45, 10, 25))

    # === TRASH ON FLOOR ===
    # Crumpled paper
    for px, py in [(125, floor_y - 5), (200, floor_y - 8), (80, floor_y - 3)]:
        pygame.draw.circle(surface, (230, 230, 235), (px, py), 4)
        pygame.draw.circle(surface, (200, 200, 205), (px, py), 2)

    # === PUDDLE ===
    pygame.draw.ellipse(surface, (100, 110, 105), (110, floor_y + 15, 45, 12))
    pygame.draw.ellipse(surface, (120, 130, 125), (115, floor_y + 17, 35, 8))

    # === DOOR ===
    door_x = 0
    pygame.draw.rect(surface, (80, 85, 90), (door_x, floor_y - 85, 30, 85))
    pygame.draw.rect(surface, (70, 75, 80), (door_x + 2, floor_y - 83, 26, 81))
    # "RESTROOM" sign
    try:
        font = pygame.font.Font(None, 10)
        sign = font.render("WC", True, (255, 255, 255))
        surface.blit(sign, (door_x + 8, floor_y - 95))
    except:
        pass

    return surface


def create_record_vault_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the rare vinyl basement vault background."""
    surface = pygame.Surface(size)
    w, h = size

    # Warm basement gradient with dust
    create_gradient(surface, [
        (45, 35, 50),
        (70, 55, 80),
        (35, 25, 45),
    ])

    # Wooden floor
    floor_y = h - 45
    floor_color = (65, 50, 40)
    pygame.draw.rect(surface, floor_color, (0, floor_y, w, 50))

    # Floorboards
    for i in range(0, w, 25):
        pygame.draw.line(surface, (55, 40, 30), (i, floor_y), (i, h), 1)
        # Wood grain
        pygame.draw.line(surface, (70, 55, 45), (i + 5, floor_y + 5), (i + 5, floor_y + 35), 1)

    # === FLOOR-TO-CEILING RECORD SHELVES ===
    # Left shelves
    shelf_color = (50, 40, 35)
    shelf_highlight = (70, 60, 50)
    record_colors = [
        (30, 30, 35), (40, 25, 25), (25, 35, 45),
        (180, 150, 120), (200, 180, 160), (35, 25, 30)
    ]

    for shelf_num in range(7):
        sy = 25 + shelf_num * 24
        # Shelf board
        pygame.draw.rect(surface, shelf_color, (5, sy, 90, 22))
        pygame.draw.rect(surface, shelf_highlight, (5, sy, 90, 3))

        # Records on shelf
        for i in range(15):
            rx = 8 + i * 6
            rc = random.choice(record_colors)
            # Slight tilt variation
            tilt = random.randint(-2, 2)
            pygame.draw.rect(surface, rc, (rx, sy + 3 + tilt, 4, 16))
            # Spine detail
            pygame.draw.line(surface, tuple(min(255, c + 20) for c in rc),
                           (rx + 1, sy + 5), (rx + 1, sy + 17), 1)

    # Right shelves
    for shelf_num in range(7):
        sy = 25 + shelf_num * 24
        pygame.draw.rect(surface, shelf_color, (w - 95, sy, 90, 22))
        pygame.draw.rect(surface, shelf_highlight, (w - 95, sy, 90, 3))

        # Records on shelf
        for i in range(15):
            rx = w - 92 + i * 6
            rc = random.choice(record_colors)
            tilt = random.randint(-2, 2)
            pygame.draw.rect(surface, rc, (rx, sy + 3 + tilt, 4, 16))
            pygame.draw.line(surface, tuple(min(255, c + 20) for c in rc),
                           (rx + 1, sy + 5), (rx + 1, sy + 17), 1)

    # Back wall shelves
    for shelf_num in range(5):
        sy = 30 + shelf_num * 28
        pygame.draw.rect(surface, shelf_color, (110, sy, 100, 26))
        pygame.draw.rect(surface, shelf_highlight, (110, sy, 100, 3))

        # Records (front-facing)
        for i in range(10):
            rx = 115 + i * 10
            album_colors = [
                (255, 200, 80), (200, 100, 150), (100, 200, 255),
                (150, 255, 150), (255, 150, 100), (180, 180, 220)
            ]
            ac = random.choice(album_colors)
            # Album cover
            pygame.draw.rect(surface, ac, (rx, sy + 4, 8, 18))
            pygame.draw.rect(surface, (30, 30, 35), (rx, sy + 4, 8, 18), 1)
            # Cover art suggestion
            pygame.draw.rect(surface, tuple(c - 50 for c in ac), (rx + 1, sy + 6, 6, 8))

    # === WOODEN LADDER ===
    ladder_x = 135
    ladder_w = 6
    # Side rails
    pygame.draw.rect(surface, (90, 70, 50), (ladder_x, 40, ladder_w, floor_y - 40))
    pygame.draw.rect(surface, (90, 70, 50), (ladder_x + 30, 40, ladder_w, floor_y - 40))
    # Rungs
    for i in range(7):
        rung_y = 50 + i * 22
        pygame.draw.rect(surface, (80, 60, 45), (ladder_x, rung_y, 36, 5))
        # Shadow
        pygame.draw.line(surface, (60, 45, 35), (ladder_x, rung_y + 5), (ladder_x + 36, rung_y + 5))

    # === DUST PARTICLES IN LIGHT ===
    # Light beam from above
    for i in range(50):
        px = random.randint(ladder_x - 30, ladder_x + 60)
        py = random.randint(20, floor_y)
        brightness = random.randint(100, 150)
        if random.random() > 0.7:
            surface.set_at((px, py), (brightness, brightness, brightness - 20))

    # === ULTRA-RARE PRESSINGS (highlighted) ===
    # Special display case
    case_x = 240
    case_y = 60
    pygame.draw.rect(surface, (80, 70, 60), (case_x, case_y, 50, 60))
    # Glass
    pygame.draw.rect(surface, (120, 130, 140), (case_x + 3, case_y + 3, 44, 54))
    # Prized record
    pygame.draw.rect(surface, (200, 150, 100), (case_x + 15, case_y + 15, 20, 30))
    pygame.draw.rect(surface, (30, 30, 35), (case_x + 15, case_y + 15, 20, 30), 1)
    # Gold record effect
    for i in range(3):
        pygame.draw.circle(surface, (255, 215, 0), (case_x + 25, case_y + 30), 8 - i * 2)

    # === CRATE-DIGGER ZOMBIE AREA ===
    # Crate on floor
    crate_x = 20
    pygame.draw.rect(surface, (70, 55, 45), (crate_x, floor_y - 35, 55, 35))
    pygame.draw.rect(surface, (60, 45, 35), (crate_x + 2, floor_y - 33, 51, 31))
    # Records in crate
    for i in range(8):
        rx = crate_x + 5 + i * 6
        pygame.draw.rect(surface, (35, 30, 35), (rx, floor_y - 30, 4, 25))

    # === LISTENING STATION ===
    station_x = w - 85
    # Table
    pygame.draw.rect(surface, (65, 50, 45), (station_x, floor_y - 45, 60, 45))
    pygame.draw.rect(surface, (75, 60, 55), (station_x, floor_y - 45, 60, 4))
    # Turntable
    pygame.draw.circle(surface, (40, 40, 45), (station_x + 30, floor_y - 25), 15)
    pygame.draw.circle(surface, (60, 60, 65), (station_x + 30, floor_y - 25), 10)
    pygame.draw.circle(surface, (100, 100, 110), (station_x + 30, floor_y - 25), 3)
    # Tonearm
    pygame.draw.line(surface, (120, 120, 130), (station_x + 30, floor_y - 25),
                    (station_x + 45, floor_y - 35), 2)

    # === VINTAGE RECORD PLAYER ===
    player_x = 25
    player_y = floor_y - 100
    pygame.draw.rect(surface, (80, 60, 50), (player_x, player_y, 45, 25))
    # Speaker grill
    pygame.draw.rect(surface, (50, 40, 35), (player_x + 5, player_y + 5, 35, 15))
    for i in range(7):
        pygame.draw.line(surface, (70, 60, 55), (player_x + 7 + i * 5, player_y + 6),
                        (player_x + 7 + i * 5, player_y + 19))

    # === PRICE TAGS ===
    tags = [(150, 70), (180, 95), (130, 120)]
    for tx, ty in tags:
        try:
            font = pygame.font.Font(None, 10)
            price = font.render("$" + str(random.choice([15, 25, 50, 100])), True, (255, 200, 100))
            surface.blit(price, (tx, ty))
        except:
            pass

    # === DOOR ===
    pygame.draw.rect(surface, (60, 50, 45), (0, floor_y - 80, 26, 80))
    pygame.draw.rect(surface, (50, 40, 35), (2, floor_y - 78, 22, 76))
    # "VAULT" sign
    try:
        font = pygame.font.Font(None, 12)
        sign = font.render("VAULT", True, (200, 180, 100))
        surface.blit(sign, (3, floor_y - 95))
    except:
        pass

    return surface


def create_promoter_office_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the upstairs promoter's office - the villain's lair."""
    surface = pygame.Surface(size)
    w, h = size

    # Ominous red-tinted gradient
    create_gradient(surface, [
        (50, 20, 35),
        (90, 40, 70),
        (40, 15, 30),
    ])

    # Carpet floor
    floor_y = h - 50
    carpet_color = (80, 30, 50)
    pygame.draw.rect(surface, carpet_color, (0, floor_y, w, 55))
    # Carpet texture
    for i in range(30):
        cx = random.randint(0, w)
        cy = random.randint(floor_y, h)
        pygame.draw.circle(surface, (85, 35, 55), (cx, cy), 1)

    # Wood-paneled walls
    wall_color = (60, 45, 40)
    pygame.draw.rect(surface, wall_color, (0, 20, w, floor_y - 20))
    # Wood panels
    for i in range(0, w, 35):
        pygame.draw.line(surface, (50, 35, 30), (i, 20), (i, floor_y), 2)

    # === MASSIVE DESK ===
    desk_x = 80
    desk_w = 160
    desk_h = 50
    desk_y = floor_y - desk_h

    # Desk surface
    pygame.draw.rect(surface, (70, 50, 40), (desk_x, desk_y, desk_w, desk_h))
    pygame.draw.rect(surface, (90, 70, 60), (desk_x, desk_y, desk_w, 5))
    # Leather inlay
    pygame.draw.rect(surface, (40, 70, 50), (desk_x + 20, desk_y + 8, desk_w - 40, 30))

    # Desk legs
    pygame.draw.rect(surface, (60, 45, 35), (desk_x + 10, floor_y - 5, 12, 8))
    pygame.draw.rect(surface, (60, 45, 35), (desk_x + desk_w - 22, floor_y - 5, 12, 8))

    # === CONTRACTS ON DESK ===
    # Stack of papers
    for i in range(5):
        paper_color = (240, 235, 220)
        pygame.draw.rect(surface, paper_color, (desk_x + 30 + i * 2, desk_y + 12 - i, 35, 25))
        pygame.draw.rect(surface, (30, 30, 35), (desk_x + 30 + i * 2, desk_y + 12 - i, 35, 25), 1)
        # Text lines
        for j in range(4):
            pygame.draw.line(surface, (50, 50, 60),
                           (desk_x + 33 + i * 2, desk_y + 17 - i + j * 4),
                           (desk_x + 60 + i * 2, desk_y + 17 - i + j * 4), 1)

    # === ROTARY PHONE ===
    phone_x = desk_x + 100
    # Phone base
    pygame.draw.rect(surface, (30, 30, 35), (phone_x, desk_y + 15, 25, 12))
    # Handset
    pygame.draw.ellipse(surface, (35, 35, 40), (phone_x + 5, desk_y + 10, 8, 4))
    pygame.draw.rect(surface, (35, 35, 40), (phone_x + 8, desk_y + 8, 2, 8))
    pygame.draw.ellipse(surface, (35, 35, 40), (phone_x + 5, desk_y + 14, 8, 4))
    # Rotary dial
    pygame.draw.circle(surface, (25, 25, 30), (phone_x + 12, desk_y + 20), 6)
    pygame.draw.circle(surface, (40, 40, 45), (phone_x + 12, desk_y + 20), 4)

    # === POSTERS ON WALL ===
    poster_data = [
        (20, 40, (255, 180, 60), "SOLD OUT"),
        (250, 45, (200, 100, 200), "TONIGHT"),
    ]

    for px, py, color, text in poster_data:
        pygame.draw.rect(surface, color, (px, py, 45, 55))
        pygame.draw.rect(surface, (30, 30, 40), (px, py, 45, 55), 1)
        # Poster image
        pygame.draw.rect(surface, tuple(c - 50 for c in color), (px + 5, py + 8, 35, 30))
        try:
            font = pygame.font.Font(None, 10)
            label = font.render(text, True, (255, 255, 255))
            surface.blit(label, (px + 8, py + 42))
        except:
            pass

    # === GOLD RECORDS ON WALL ===
    gold_positions = [(100, 35), (180, 38)]
    for gx, gy in gold_positions:
        # Frame
        pygame.draw.rect(surface, (100, 80, 60), (gx, gy, 35, 45))
        pygame.draw.rect(surface, (120, 100, 80), (gx + 2, gy + 2, 31, 41))
        # Gold record
        pygame.draw.circle(surface, (255, 215, 0), (gx + 17, gy + 18), 12)
        pygame.draw.circle(surface, (200, 170, 0), (gx + 17, gy + 18), 8)
        pygame.draw.circle(surface, (100, 80, 60), (gx + 17, gy + 18), 3)
        # Plaque
        pygame.draw.rect(surface, (180, 160, 120), (gx + 5, gy + 32, 25, 8))

    # === OCCULT SYMBOLS (hidden in decor) ===
    # Pentagram in carpet pattern (subtle)
    symbol_x = w - 60
    symbol_y = floor_y + 20
    points = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = symbol_x + int(15 * math.cos(angle))
        py = symbol_y + int(15 * math.sin(angle))
        points.append((px, py))
    # Draw faintly
    for i in range(5):
        pygame.draw.line(surface, (100, 40, 60), points[i], points[(i + 2) % 5], 1)

    # === BOOKSHELF ===
    shelf_x = w - 85
    pygame.draw.rect(surface, (50, 40, 35), (shelf_x, floor_y - 90, 75, 90))
    # Shelves
    for i in range(4):
        sy = floor_y - 85 + i * 22
        pygame.draw.rect(surface, (60, 50, 45), (shelf_x + 3, sy, 69, 3))
        # Books
        for j in range(8):
            bx = shelf_x + 6 + j * 8
            book_colors = [(150, 50, 50), (50, 50, 100), (80, 60, 40), (40, 80, 60)]
            bc = random.choice(book_colors)
            pygame.draw.rect(surface, bc, (bx, sy + 4, 6, 16))
            # Spine
            pygame.draw.line(surface, tuple(min(255, c + 30) for c in bc),
                           (bx + 1, sy + 5), (bx + 1, sy + 19), 1)

    # === LEATHER CHAIR ===
    chair_x = desk_x + 60
    chair_y = floor_y - 65
    # Chair back
    pygame.draw.rect(surface, (80, 30, 30), (chair_x, chair_y, 40, 50))
    pygame.draw.rect(surface, (100, 40, 40), (chair_x + 3, chair_y + 3, 34, 44))
    # Tufted pattern
    for row in range(3):
        for col in range(3):
            tx = chair_x + 10 + col * 10
            ty = chair_y + 10 + row * 12
            pygame.draw.circle(surface, (70, 25, 25), (tx, ty), 2)

    # Chair seat
    pygame.draw.rect(surface, (90, 35, 35), (chair_x - 5, floor_y - 20, 50, 20))
    # Chair legs
    pygame.draw.rect(surface, (60, 50, 45), (chair_x + 5, floor_y - 5, 8, 8))
    pygame.draw.rect(surface, (60, 50, 45), (chair_x + 32, floor_y - 5, 8, 8))

    # === WHISKEY DECANTER ===
    decanter_x = desk_x + 130
    # Decanter
    pygame.draw.rect(surface, (150, 100, 50), (decanter_x, desk_y + 18, 12, 18))
    pygame.draw.polygon(surface, (150, 100, 50), [
        (decanter_x + 4, desk_y + 18),
        (decanter_x + 8, desk_y + 18),
        (decanter_x + 6, desk_y + 12)
    ])
    # Liquid
    pygame.draw.rect(surface, (180, 120, 40), (decanter_x + 2, desk_y + 25, 8, 10))
    # Glass
    pygame.draw.rect(surface, (180, 180, 190), (decanter_x + 15, desk_y + 22, 8, 12))
    pygame.draw.rect(surface, (180, 120, 40), (decanter_x + 16, desk_y + 27, 6, 6))

    # === WINDOW ===
    window_x = 10
    window_y = 35
    pygame.draw.rect(surface, (20, 15, 30), (window_x, window_y, 50, 60))
    # Window panes
    pygame.draw.line(surface, (80, 70, 60), (window_x, window_y + 30), (window_x + 50, window_y + 30), 2)
    pygame.draw.line(surface, (80, 70, 60), (window_x + 25, window_y), (window_x + 25, window_y + 60), 2)
    # City lights outside
    for i in range(8):
        lx = window_x + random.randint(5, 45)
        ly = window_y + random.randint(5, 55)
        light_color = random.choice([(255, 200, 100), (100, 200, 255), (255, 100, 200)])
        pygame.draw.circle(surface, light_color, (lx, ly), 2)

    # === DOOR ===
    pygame.draw.rect(surface, (70, 55, 50), (w - 35, floor_y - 85, 35, 85))
    pygame.draw.rect(surface, (60, 45, 40), (w - 33, floor_y - 83, 31, 81))
    # Door handle
    pygame.draw.circle(surface, (180, 160, 120), (w - 30, floor_y - 42), 3)
    # "PRIVATE" sign
    try:
        font = pygame.font.Font(None, 11)
        sign = font.render("PRIVATE", True, (200, 50, 50))
        surface.blit(sign, (w - 32, floor_y - 95))
    except:
        pass

    return surface


def create_loading_dock_background(size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Create the loading dock background with equipment trucks."""
    surface = pygame.Surface(size)
    w, h = size

    # Night sky gradient
    create_gradient(surface, [
        (15, 10, 25),
        (30, 20, 45),
        (20, 15, 30),
    ])

    # Stars
    draw_stars(surface, 30)

    # Asphalt ground
    floor_y = h - 60
    pygame.draw.rect(surface, (40, 40, 45), (0, floor_y, w, 65))

    # Pavement cracks
    crack_paths = [
        [(0, floor_y + 20), (80, floor_y + 25), (160, floor_y + 18)],
        [(200, floor_y + 30), (280, floor_y + 28), (320, floor_y + 35)],
    ]
    for path in crack_paths:
        pygame.draw.lines(surface, (30, 30, 35), False, path, 2)

    # === LOADING DOCK PLATFORM ===
    dock_y = floor_y - 25
    pygame.draw.rect(surface, (60, 55, 65), (0, dock_y, 120, 25))
    pygame.draw.rect(surface, (70, 65, 75), (0, dock_y, 120, 3))
    # Metal edge
    pygame.draw.rect(surface, (100, 100, 110), (0, dock_y + 24, 120, 2))

    # === SEMI-TRUCK ===
    truck_x = 140
    # Trailer
    pygame.draw.rect(surface, (200, 200, 210), (truck_x, floor_y - 70, 140, 70))
    pygame.draw.rect(surface, (180, 180, 190), (truck_x + 2, floor_y - 68, 136, 66))

    # Band logo on truck
    logo_x = truck_x + 40
    logo_y = floor_y - 50
    # "THE NEON DEAD" logo
    pygame.draw.rect(surface, (255, 100, 200), (logo_x, logo_y, 60, 30))
    pygame.draw.rect(surface, (30, 30, 40), (logo_x, logo_y, 60, 30), 2)
    try:
        font = pygame.font.Font(None, 12)
        logo = font.render("NEON", True, (255, 255, 255))
        surface.blit(logo, (logo_x + 12, logo_y + 5))
        logo2 = font.render("DEAD", True, (255, 255, 255))
        surface.blit(logo2, (logo_x + 12, logo_y + 15))
    except:
        pass

    # Trailer wheels
    for wx in [truck_x + 20, truck_x + 50, truck_x + 110]:
        pygame.draw.circle(surface, (30, 30, 35), (wx, floor_y - 2), 8)
        pygame.draw.circle(surface, (50, 50, 55), (wx, floor_y - 2), 5)
        pygame.draw.circle(surface, (70, 70, 75), (wx, floor_y - 2), 2)

    # Cab
    cab_x = truck_x - 40
    pygame.draw.rect(surface, (180, 50, 50), (cab_x, floor_y - 65, 42, 40))
    pygame.draw.rect(surface, (200, 60, 60), (cab_x + 2, floor_y - 63, 38, 36))
    # Windshield
    pygame.draw.rect(surface, (60, 80, 100), (cab_x + 5, floor_y - 60, 32, 20))
    # Grill
    pygame.draw.rect(surface, (100, 100, 110), (cab_x + 8, floor_y - 35, 26, 8))
    # Headlights
    pygame.draw.circle(surface, (255, 240, 180), (cab_x + 10, floor_y - 20), 4)
    pygame.draw.circle(surface, (255, 240, 180), (cab_x + 32, floor_y - 20), 4)
    # Cab wheels
    pygame.draw.circle(surface, (30, 30, 35), (cab_x + 12, floor_y - 2), 8)
    pygame.draw.circle(surface, (50, 50, 55), (cab_x + 12, floor_y - 2), 5)

    # === ROAD CASES ===
    cases = [
        (20, floor_y - 50, 35, 50),
        (60, floor_y - 45, 40, 45),
        (25, floor_y - 105, 38, 45),
    ]

    for cx, cy, cw, ch in cases:
        # Case body
        pygame.draw.rect(surface, (30, 30, 35), (cx, cy, cw, ch))
        pygame.draw.rect(surface, (50, 50, 55), (cx, cy, cw, 4))
        # Metal corners
        for corner in [(cx, cy), (cx + cw - 5, cy), (cx, cy + ch - 5), (cx + cw - 5, cy + ch - 5)]:
            pygame.draw.rect(surface, (120, 120, 130), (corner[0], corner[1], 5, 5))
        # Handle
        pygame.draw.rect(surface, (150, 140, 120), (cx + cw // 2 - 8, cy + ch - 15, 16, 4))
        # Latches
        pygame.draw.rect(surface, (150, 140, 120), (cx + cw - 8, cy + ch // 2 - 3, 6, 6))
        # Labels/stickers
        if random.random() > 0.5:
            sticker_color = random.choice([(255, 200, 100), (100, 255, 200), (255, 100, 200)])
            pygame.draw.rect(surface, sticker_color, (cx + 5, cy + 8, 15, 10))

    # === CABLES ===
    cable_coils = [(110, floor_y - 15), (85, floor_y - 8)]
    for coil_x, coil_y in cable_coils:
        for i in range(4):
            pygame.draw.circle(surface, (30, 30, 35), (coil_x + i * 2, coil_y + i), 8, 2)

    # === DOLLY ===
    dolly_x = 75
    # Platform
    pygame.draw.rect(surface, (80, 80, 90), (dolly_x, floor_y - 12, 30, 12))
    # Handle
    pygame.draw.rect(surface, (70, 70, 80), (dolly_x + 13, floor_y - 50, 4, 38))
    pygame.draw.rect(surface, (70, 70, 80), (dolly_x + 5, floor_y - 52, 20, 4))
    # Wheels
    pygame.draw.circle(surface, (40, 40, 45), (dolly_x + 8, floor_y - 2), 5)
    pygame.draw.circle(surface, (40, 40, 45), (dolly_x + 22, floor_y - 2), 5)

    # === SECURITY LIGHT ===
    light_x = 30
    # Pole
    pygame.draw.rect(surface, (70, 70, 80), (light_x, floor_y - 120, 5, 120))
    # Light fixture
    pygame.draw.rect(surface, (90, 90, 100), (light_x - 8, floor_y - 135, 21, 15))
    # Light glow
    for i in range(6):
        alpha = 180 - i * 25
        pygame.draw.circle(surface, (255, 240, 180), (light_x + 2, floor_y - 125), 15 + i * 8)

    # === BUILDING WALL ===
    wall_color = (45, 40, 55)
    pygame.draw.rect(surface, wall_color, (0, 20, 130, dock_y - 20))

    # Brick texture
    brick_w, brick_h = 20, 10
    for row in range(15):
        offset = (row % 2) * 10
        for col in range(8):
            bx = col * brick_w + offset
            by = 20 + row * brick_h
            if bx < 130:
                pygame.draw.rect(surface, wall_color, (bx, by, brick_w - 1, brick_h - 1))
                pygame.draw.rect(surface, (55, 50, 65), (bx, by, brick_w - 1, 2))

    # Overhead door
    door_x = 10
    door_y = dock_y - 80
    pygame.draw.rect(surface, (100, 100, 110), (door_x, door_y, 90, 80))
    # Door panels
    for i in range(8):
        panel_y = door_y + 3 + i * 9
        pygame.draw.rect(surface, (90, 90, 100), (door_x + 3, panel_y, 84, 8))

    # === EXIT SIGN ===
    exit_x = 105
    exit_y = dock_y - 35
    pygame.draw.rect(surface, (50, 255, 50), (exit_x, exit_y, 20, 10))
    try:
        font = pygame.font.Font(None, 10)
        exit_text = font.render("EXIT", True, (255, 255, 255))
        surface.blit(exit_text, (exit_x + 2, exit_y + 1))
    except:
        pass

    # === ZOMBIE ROADIE SILHOUETTE ===
    zombie_x = 250
    # Shambling posture
    pygame.draw.ellipse(surface, (60, 60, 70), (zombie_x, floor_y - 35, 15, 8))  # head
    pygame.draw.rect(surface, (55, 55, 65), (zombie_x + 3, floor_y - 30, 9, 20))  # body
    # Arms (one holding cable)
    pygame.draw.line(surface, (55, 55, 65), (zombie_x + 5, floor_y - 25), (zombie_x - 5, floor_y - 15), 3)
    pygame.draw.line(surface, (55, 55, 65), (zombie_x + 10, floor_y - 25), (zombie_x + 18, floor_y - 18), 3)
    # Cable in hand
    cable_path = [(zombie_x + 18, floor_y - 18), (zombie_x + 20, floor_y - 10), (zombie_x + 22, floor_y - 5)]
    pygame.draw.lines(surface, (30, 30, 35), False, cable_path, 2)

    # === EXHAUST/SMOKE ===
    # From truck
    for i in range(5):
        smoke_x = cab_x - 5 + i * 3
        smoke_y = floor_y - 65 + i * 2
        smoke_size = 3 + i
        pygame.draw.circle(surface, (80, 80, 90), (smoke_x, smoke_y), smoke_size)

    return surface

def get_room_background(room_id: str, size: Tuple[int, int] = (320, 200)) -> pygame.Surface:
    """Get the appropriate background for a room ID."""
    generators = {
        "hennepin_outside": create_hennepin_background,
        "record_store": create_record_store_background,
        "college_station": create_radio_station_background,
        "backstage_stage": create_backstage_background,
        "green_room": create_green_room_background,
        "merch_booth": create_merch_booth_background,
        "coat_check": create_coat_check_background,
        "sound_booth": create_sound_booth_background,
        "vip_lounge": create_vip_lounge_background,
        "memorial_wall": create_memorial_wall_background,
        "main_stage": create_main_stage_background,
        "back_alley": create_back_alley_background,
        "venue_basement": create_venue_basement_background,
        "tour_bus": create_tour_bus_background,
        "rooftop": create_rooftop_background,
        "practice_space": create_practice_space_background,
        "club_bathroom": create_club_bathroom_background,
        "record_vault": create_record_vault_background,
        "promoter_office": create_promoter_office_background,
        "loading_dock": create_loading_dock_background,
    }

    generator = generators.get(room_id)
    if generator:
        return generator(size)

    # Default background
    surface = pygame.Surface(size)
    create_gradient(surface, [(30, 20, 50), (60, 40, 90), (20, 15, 35)])
    return surface
