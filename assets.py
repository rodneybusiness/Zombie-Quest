"""Placeholder asset generation utilities for the Zombie Quest SCI-style engine.

The goal of this module is to create convincing stand-in artwork so that the rest of
the game feels like a finished VGA production even without bespoke art. Every
surface that leaves this module attempts to mimic Sierra's SCI aesthetic by using
hand-tinted gradients, dithering, and chunky pixel outlines rather than flat
developer placeholders.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, List, Sequence, Tuple

import pygame

from settings import WORLD_WIDTH, WORLD_HEIGHT

_PLACEHOLDER_CACHE: Dict[str, pygame.Surface] = {}
_CHARACTER_CACHE: Dict[str, Dict[str, Dict[str, List[pygame.Surface]]]] = {}
_CURSOR_CACHE: Dict[str, pygame.Surface] = {}
_FONT_CACHE: Dict[str, pygame.font.Font] = {}
_AMBIENT_CACHE: Dict[str, List[pygame.Surface]] = {}


def get_font(name: str, size: int) -> pygame.font.Font:
    """Return a cached pygame font object."""
    key = f"{name}-{size}"
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(name, size)
    return _FONT_CACHE[key]


def _label_surface(surface: pygame.Surface, text: str, font_size: int = 18) -> None:
    """Stamp a tasteful caption onto a placeholder surface."""
    font = get_font("timesnewroman", font_size)
    text_surface = font.render(text, True, (240, 220, 180))
    outline = font.render(text, True, (10, 10, 10))
    rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(outline, rect.move(1, 1))
    surface.blit(text_surface, rect)


def _lerp_color(top: Tuple[int, int, int], bottom: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return (
        int(top[0] + (bottom[0] - top[0]) * t),
        int(top[1] + (bottom[1] - top[1]) * t),
        int(top[2] + (bottom[2] - top[2]) * t),
    )


def _apply_dither(surface: pygame.Surface, top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> None:
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        base = _lerp_color(top, bottom, t)
        for x in range(width):
            jitter = ((x ^ y) & 1) * 6 - 3
            surface.set_at((x, y), (
                max(0, min(255, base[0] + jitter)),
                max(0, min(255, base[1] + jitter)),
                max(0, min(255, base[2] + jitter)),
            ))


def _draw_clouds(surface: pygame.Surface, color: Tuple[int, int, int]) -> None:
    width, _ = surface.get_size()
    cloud_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for i in range(6):
        radius = 32 + i * 6
        x = (width // 6) * i + 24
        y = 36 + (i % 3) * 6
        pygame.draw.circle(cloud_surface, (*color, 90), (x, y), radius)
    surface.blit(cloud_surface, (0, 0))


def _draw_perspective_ground(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    horizon = height // 2 + 10
    for y in range(horizon, height):
        t = (y - horizon) / max(1, height - horizon)
        row_width = int(width * (0.35 + 0.65 * t))
        start_x = width // 2 - row_width // 2
        color = _lerp_color((40, 32, 32), (110, 70, 60), t)
        pygame.draw.line(surface, color, (start_x, y), (start_x + row_width, y))
        if y % 14 == 0:
            pygame.draw.line(surface, (0, 0, 0), (start_x, y), (start_x + row_width, y), 1)
        if y % 28 == 14:
            fade_color = _lerp_color((200, 180, 160), (120, 100, 90), t)
            pygame.draw.line(surface, fade_color, (start_x + 4, y), (start_x + row_width - 4, y), 1)


def _draw_building(surface: pygame.Surface, rect: pygame.Rect, palette: Sequence[Tuple[int, int, int]], window_rows: int = 3) -> None:
    base_color = palette[0]
    pygame.draw.rect(surface, base_color, rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)
    window_height = (rect.height - 16) // window_rows
    window_width = rect.width // 4
    window_color = palette[1]
    for row in range(window_rows):
        for col in range(3):
            wx = rect.x + 8 + col * (window_width + 4)
            wy = rect.y + 8 + row * (window_height + 6)
            window_rect = pygame.Rect(wx, wy, window_width, window_height)
            pygame.draw.rect(surface, window_color, window_rect)
            pygame.draw.rect(surface, (20, 20, 20), window_rect, 1)


def _draw_sign(surface: pygame.Surface, rect: pygame.Rect, text: str) -> None:
    pygame.draw.rect(surface, (86, 28, 26), rect)
    pygame.draw.rect(surface, (240, 220, 180), rect, 2)
    font = get_font("timesnewroman", 18)
    label = font.render(text, True, (240, 220, 180))
    outline = font.render(text, True, (10, 10, 10))
    text_rect = label.get_rect(center=rect.center)
    surface.blit(outline, text_rect.move(1, 1))
    surface.blit(label, text_rect)


def _draw_floor_tiles(surface: pygame.Surface, base_color: Tuple[int, int, int]) -> None:
    tile = pygame.Surface((16, 16))
    tile.fill(base_color)
    pygame.draw.rect(tile, (0, 0, 0), tile.get_rect(), 1)
    darker = pygame.Color(max(base_color[0] - 20, 0), max(base_color[1] - 20, 0), max(base_color[2] - 20, 0))
    pygame.draw.rect(tile, darker, (0, 0, 8, 8))
    pygame.draw.rect(tile, darker, (8, 8, 8, 8))
    for x in range(0, surface.get_width(), tile.get_width()):
        for y in range(0, surface.get_height(), tile.get_height()):
            surface.blit(tile, (x, y))


def _build_street_scene(surface: pygame.Surface, name: str) -> None:
    _apply_dither(surface, (18, 30, 66), (48, 64, 120))
    _draw_clouds(surface, (240, 240, 255))

    horizon = pygame.Rect(0, 88, WORLD_WIDTH, WORLD_HEIGHT - 88)
    ground = pygame.Surface(horizon.size, pygame.SRCALPHA)
    _draw_perspective_ground(ground)
    surface.blit(ground, horizon)

    mid_building = pygame.Rect(96, 46, 148, 102)
    right_building = pygame.Rect(222, 54, 84, 94)
    left_building = pygame.Rect(16, 64, 94, 90)
    _draw_building(surface, left_building, [(54, 66, 92), (184, 188, 204)])
    _draw_building(surface, mid_building, [(78, 48, 48), (230, 190, 140)])
    _draw_building(surface, right_building, [(32, 54, 74), (180, 210, 220)])

    awning = pygame.Rect(mid_building.x + 4, mid_building.y + 44, mid_building.width - 8, 18)
    pygame.draw.rect(surface, (140, 28, 36), awning)
    for stripe in range(0, awning.width, 8):
        pygame.draw.rect(surface, (220, 196, 160), (awning.x + stripe, awning.y, 4, awning.height))
    pygame.draw.rect(surface, (0, 0, 0), awning, 2)

    sign_rect = pygame.Rect(right_building.x + 6, right_building.y + 12, right_building.width - 12, 28)
    _draw_sign(surface, sign_rect, "QUIET FALLS")

    dumpster_rect = pygame.Rect(32, 138, 96, 44)
    pygame.draw.rect(surface, (28, 60, 56), dumpster_rect)
    pygame.draw.rect(surface, (8, 20, 18), dumpster_rect, 2)
    pygame.draw.rect(surface, (64, 120, 112), dumpster_rect.inflate(-12, -16))
    pygame.draw.line(surface, (12, 32, 30), (dumpster_rect.left, dumpster_rect.top + 10), (dumpster_rect.right, dumpster_rect.top + 6), 3)

    marquee_rect = pygame.Rect(214, 136, 96, 40)
    pygame.draw.rect(surface, (96, 34, 32), marquee_rect)
    pygame.draw.rect(surface, (220, 208, 200), marquee_rect, 3)
    marquee_font = get_font("timesnewroman", 16)
    marquee_text = marquee_font.render("DINER", True, (240, 220, 200))
    surface.blit(marquee_text, marquee_text.get_rect(center=marquee_rect.center))

    pygame.draw.ellipse(surface, (70, 90, 120), pygame.Rect(46, 156, 86, 24))
    pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(46, 156, 86, 24), 1)
    for i in range(4):
        line_width = 12 + i * 2
        y = 170 + i * 6
        pygame.draw.line(surface, (240, 200, 120), (WORLD_WIDTH // 2 - line_width, y), (WORLD_WIDTH // 2 + line_width, y), 2)

    if name.endswith("_night"):
        tint = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        tint.fill((12, 18, 40, 90))
        surface.blit(tint, (0, 0))


def _build_diner_interior(surface: pygame.Surface) -> None:
    _apply_dither(surface, (26, 18, 38), (54, 24, 58))
    ceiling_rect = pygame.Rect(0, 0, WORLD_WIDTH, 52)
    pygame.draw.rect(surface, (68, 60, 82), ceiling_rect)
    pygame.draw.line(surface, (0, 0, 0), ceiling_rect.bottomleft, ceiling_rect.bottomright, 2)

    wall = pygame.Rect(0, ceiling_rect.bottom, WORLD_WIDTH, 84)
    _draw_floor_tiles(surface.subsurface(wall), (104, 44, 64))
    pygame.draw.rect(surface, (0, 0, 0), wall, 2)

    booths = [
        pygame.Rect(24, wall.bottom - 32, 84, 46),
        pygame.Rect(122, wall.bottom - 26, 92, 52),
        pygame.Rect(224, wall.bottom - 40, 84, 58),
    ]
    for booth in booths:
        pygame.draw.rect(surface, (140, 40, 40), booth)
        pygame.draw.rect(surface, (60, 12, 12), booth, 3)
        cushion = booth.inflate(-12, -18)
        pygame.draw.rect(surface, (200, 120, 120), cushion)
        pygame.draw.rect(surface, (80, 20, 30), cushion, 2)

    counter = pygame.Rect(0, wall.bottom - 12, WORLD_WIDTH, WORLD_HEIGHT - (wall.bottom - 12))
    counter_surface = pygame.Surface(counter.size)
    _draw_floor_tiles(counter_surface, (56, 36, 36))
    surface.blit(counter_surface, counter.topleft)
    pygame.draw.rect(surface, (0, 0, 0), counter, 2)

    for i in range(7):
        lamp_x = 24 + i * 44
        pygame.draw.line(surface, (30, 16, 16), (lamp_x, 4), (lamp_x, 44), 2)
        pygame.draw.circle(surface, (240, 180, 120), (lamp_x, 48), 10)
        pygame.draw.circle(surface, (0, 0, 0), (lamp_x, 48), 10, 1)

    window = pygame.Rect(76, 60, 168, 46)
    pygame.draw.rect(surface, (26, 46, 86), window)
    pygame.draw.rect(surface, (0, 0, 0), window, 2)
    for i in range(1, 4):
        pygame.draw.line(surface, (0, 0, 0), (window.x + i * 42, window.y), (window.x + i * 42, window.bottom), 2)
    for i in range(1, 3):
        pygame.draw.line(surface, (0, 0, 0), (window.x, window.y + i * 14), (window.right, window.y + i * 14), 2)

    neon_rect = pygame.Rect(200, 68, 84, 24)
    pygame.draw.rect(surface, (200, 52, 96), neon_rect, border_radius=6)
    pygame.draw.rect(surface, (0, 0, 0), neon_rect, 2)
    font = get_font("timesnewroman", 18)
    text = font.render("OPEN", True, (255, 255, 210))
    surface.blit(text, text.get_rect(center=neon_rect.center))


def _build_generic_scene(surface: pygame.Surface, name: str) -> None:
    _apply_dither(surface, (32, 42, 82), (62, 92, 140))
    hill = pygame.Rect(0, 92, WORLD_WIDTH, WORLD_HEIGHT - 92)
    pygame.draw.rect(surface, (46, 72, 62), hill)
    pygame.draw.polygon(surface, (24, 34, 28), [(0, WORLD_HEIGHT), (WORLD_WIDTH // 2, 112), (WORLD_WIDTH, WORLD_HEIGHT)])
    for i in range(6):
        x = 32 + i * 48
        pygame.draw.rect(surface, (70, 50, 60), pygame.Rect(x, 108, 30, 54))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(x, 108, 30, 54), 2)
    _label_surface(surface, f"{name.title()} Scene", font_size=18)


def create_placeholder_background(name: str) -> pygame.Surface:
    """Create a Sierra-inspired placeholder background surface.

    The returned surface is intentionally ornate so the prototype feels close to
    production. Each background shares a sky gradient, layered buildings, and a
    richly textured cobblestone street to showcase character scaling.
    """
    cache_key = f"background:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    if name.startswith("street"):
        _build_street_scene(surface, name)
    elif "diner" in name:
        _build_diner_interior(surface)
    else:
        _build_generic_scene(surface, name)

    _label_surface(surface, f"{name.replace('_', ' ').title()}", font_size=20)
    _PLACEHOLDER_CACHE[cache_key] = surface
    return surface.copy()


def create_priority_mask(name: str) -> pygame.Surface:
    cache_key = f"priority:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    mask = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    mask.fill((0, 0, 0))
    if name.startswith("street"):
        awning_region = [(104, 86), (220, 86), (212, 132), (116, 132)]
        pygame.draw.polygon(mask, (255, 255, 255), awning_region)
        marquee = [(216, 70), (306, 70), (306, 144), (216, 144)]
        pygame.draw.polygon(mask, (255, 255, 255), marquee)
        foreground_crate = [(32, 138), (100, 132), (112, 188), (24, 192)]
        pygame.draw.polygon(mask, (255, 255, 255), foreground_crate)
    else:
        counter = pygame.Rect(0, 152, WORLD_WIDTH, 48)
        pygame.draw.rect(mask, (255, 255, 255), counter)
        booths = [
            pygame.Rect(20, 132, 88, 60),
            pygame.Rect(116, 136, 96, 56),
            pygame.Rect(214, 128, 90, 68),
        ]
        for booth in booths:
            pygame.draw.rect(mask, (255, 255, 255), booth)
    _PLACEHOLDER_CACHE[cache_key] = mask
    return mask.copy()


def create_walkable_mask(name: str) -> pygame.Surface:
    cache_key = f"walkable:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    mask = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    mask.fill((0, 0, 0))
    if name.startswith("street"):
        horizon = WORLD_HEIGHT // 2 + 8
        for y in range(horizon, WORLD_HEIGHT):
            t = (y - horizon) / max(1, WORLD_HEIGHT - horizon)
            row_width = int(WORLD_WIDTH * (0.32 + 0.62 * t))
            start_x = WORLD_WIDTH // 2 - row_width // 2
            pygame.draw.line(mask, (255, 255, 255), (start_x, y), (start_x + row_width, y))

        pygame.draw.rect(mask, (0, 0, 0), pygame.Rect(44, 150, 70, 32))
        pygame.draw.rect(mask, (0, 0, 0), pygame.Rect(214, 144, 64, 40))
    else:
        walk_area = pygame.Rect(12, 136, WORLD_WIDTH - 24, 56)
        pygame.draw.rect(mask, (255, 255, 255), walk_area)
        for pillar_x in (60, 158, 254):
            pygame.draw.rect(mask, (0, 0, 0), pygame.Rect(pillar_x, 128, 10, 60))
    _PLACEHOLDER_CACHE[cache_key] = mask
    return mask.copy()


def create_priority_overlay(background: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    """Build an overlay surface that renders masked foreground elements."""
    overlay = pygame.Surface(background.get_size(), pygame.SRCALPHA)
    width, height = background.get_size()
    for y in range(height):
        for x in range(width):
            if mask.get_at((x, y))[0] > 127:
                color = background.get_at((x, y))
                overlay.set_at((x, y), (*color[:3], 255))
    return overlay.convert_alpha()


def create_neon_frames(label: str, size: Tuple[int, int], palette: Sequence[Tuple[int, int, int]]) -> List[pygame.Surface]:
    cache_key = f"neon:{label}:{size}:{palette}"
    if cache_key in _AMBIENT_CACHE:
        return [frame.copy() for frame in _AMBIENT_CACHE[cache_key]]

    frames: List[pygame.Surface] = []
    font = get_font("timesnewroman", max(12, size[1] - 8))
    outline_color = (12, 4, 12)
    for index, color in enumerate(palette):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        rect = surface.get_rect()
        glow_alpha = 90 + index * 30
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, max(10, min(220, glow_alpha))), rect.inflate(-2, -2), border_radius=rect.height // 2)
        surface.blit(glow, (0, 0))
        pygame.draw.rect(surface, (*color, 220), rect.inflate(-4, -4), border_radius=rect.height // 2)
        pygame.draw.rect(surface, outline_color, rect, 2, border_radius=rect.height // 2)
        text = font.render(label, True, (255, 252, 234))
        outline = font.render(label, True, (24, 12, 18))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(outline, text_rect.move(1, 1))
        surface.blit(text, text_rect)
        frames.append(surface)

    _AMBIENT_CACHE[cache_key] = frames
    return [frame.copy() for frame in frames]


def create_rain_texture(name: str, size: Tuple[int, int], density: float) -> pygame.Surface:
    cache_key = f"rain:{name}:{size}:{density:.2f}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    surface = pygame.Surface(size, pygame.SRCALPHA)
    drop_count = int(size[0] * density)
    for _ in range(drop_count):
        x = random.randint(0, size[0] - 1)
        length = random.randint(18, 42)
        alpha = random.randint(80, 160)
        color = (180, 210, 240, alpha)
        pygame.draw.line(surface, color, (x, 0), (x - 3, length), 1)
        pygame.draw.line(surface, (120, 160, 220, alpha // 2), (x, length // 2), (x - 2, length), 1)
    _PLACEHOLDER_CACHE[cache_key] = surface
    return surface.copy()


def _direction_color(direction: str) -> pygame.Color:
    base = {
        "down": (186, 90, 96),
        "up": (84, 132, 190),
        "left": (118, 170, 104),
        "right": (204, 158, 94),
    }[direction]
    jitter = random.randint(-8, 8)
    return pygame.Color(
        max(min(base[0] + jitter, 255), 0),
        max(min(base[1] + jitter, 255), 0),
        max(min(base[2] + jitter, 255), 0),
    )


def load_character_animations(
    name: str,
    frame_size: Tuple[int, int] = (32, 64),
    frames_per_direction: int = 4,
) -> Dict[str, Dict[str, List[pygame.Surface]]]:
    """Return cached placeholder animations for the requested character."""
    if name in _CHARACTER_CACHE:
        return {state: {direction: [frame.copy() for frame in frames] for direction, frames in dirs.items()} for state, dirs in _CHARACTER_CACHE[name].items()}

    font = get_font("arial", 10)
    directions = ["down", "up", "left", "right"]
    animations: Dict[str, Dict[str, List[pygame.Surface]]] = {"walk": {}, "idle": {}}
    name_lower = name.lower()
    torso_palettes = {
        "hero": [(186, 90, 96), (160, 104, 186), (120, 156, 212), (212, 156, 120)],
        "zombie": [(92, 140, 96), (108, 156, 88), (120, 120, 80), (86, 124, 66)],
    }
    boot_color = pygame.Color(24, 18, 16)
    accent_color = pygame.Color(240, 232, 200) if name_lower == "hero" else pygame.Color(180, 220, 180)
    for direction in directions:
        frames: List[pygame.Surface] = []
        for i in range(frames_per_direction):
            frame = pygame.Surface(frame_size, pygame.SRCALPHA)
            frame.fill((0, 0, 0, 0))
            torso_rect = pygame.Rect(6, 14, frame_size[0] - 12, frame_size[1] - 22)
            palette = torso_palettes.get(name_lower, None)
            if palette:
                torso_color = pygame.Color(*palette[directions.index(direction)])
            else:
                torso_color = _direction_color(direction)
            pygame.draw.rect(frame, torso_color, torso_rect, border_radius=6)
            highlight = pygame.Surface(torso_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 40), highlight.get_rect(), border_radius=6)
            frame.blit(highlight, torso_rect.topleft)

            sleeve_color = pygame.Color(max(torso_color.r - 40, 0), max(torso_color.g - 40, 0), max(torso_color.b - 40, 0))
            pygame.draw.rect(frame, sleeve_color, pygame.Rect(torso_rect.left - 4, torso_rect.top + 4, 10, torso_rect.height - 8), 3)
            pygame.draw.rect(frame, sleeve_color, pygame.Rect(torso_rect.right - 6, torso_rect.top + 4, 10, torso_rect.height - 8), 3)

            leg_color = pygame.Color(40, 50, 70)
            leg_rect = pygame.Rect(8 + (i % 2) * 2, frame_size[1] - 18, frame_size[0] - 16, 12)
            pygame.draw.rect(frame, leg_color, leg_rect, border_radius=4)

            pygame.draw.rect(frame, boot_color, pygame.Rect(leg_rect.left, leg_rect.bottom - 4, 10, 6), border_radius=2)
            pygame.draw.rect(frame, boot_color, pygame.Rect(leg_rect.right - 10, leg_rect.bottom - 4, 10, 6), border_radius=2)

            head_rect = pygame.Rect(frame_size[0] // 2 - 8, 4, 16, 16)
            head_color = (240, 206, 188) if name_lower == "hero" else (180, 190, 164)
            pygame.draw.ellipse(frame, head_color, head_rect)
            pygame.draw.rect(frame, (0, 0, 0), head_rect, 1)

            eye_y = head_rect.y + 6
            if direction in {"left", "right"}:
                offset = -2 if direction == "left" else 2
                pygame.draw.circle(frame, (0, 0, 0), (head_rect.centerx + offset, eye_y), 2)
            else:
                pygame.draw.circle(frame, (0, 0, 0), (head_rect.centerx - 3, eye_y), 2)
                pygame.draw.circle(frame, (0, 0, 0), (head_rect.centerx + 3, eye_y), 2)

            label = font.render(name[:3], True, accent_color)
            shadow = font.render(name[:3], True, (10, 10, 10))
            frame.blit(shadow, (5, frame_size[1] // 2 - 5))
            frame.blit(label, (4, frame_size[1] // 2 - 6))
            frames.append(frame)
        animations["walk"][direction] = frames
        animations["idle"][direction] = [frames[0]]

    _CHARACTER_CACHE[name] = animations
    return load_character_animations(name, frame_size, frames_per_direction)


def _draw_icon_background(surface: pygame.Surface, color: pygame.Color) -> None:
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        shade = pygame.Color(
            max(min(int(color.r * (0.8 + 0.4 * t)), 255), 0),
            max(min(int(color.g * (0.8 + 0.4 * t)), 255), 0),
            max(min(int(color.b * (0.8 + 0.4 * t)), 255), 0),
        )
        pygame.draw.line(surface, shade, (0, y), (width, y))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)


def create_ui_icon(label: str, size: pygame.Vector2, color: pygame.Color) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    _draw_icon_background(surface, color)
    font = get_font("timesnewroman", 16)
    text = font.render(label, True, (255, 240, 210))
    outline = font.render(label, True, (16, 16, 16))
    rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(outline, rect.move(1, 1))
    surface.blit(text, rect)
    return surface


def get_cursor_icon(verb: str) -> pygame.Surface:
    if verb in _CURSOR_CACHE:
        return _CURSOR_CACHE[verb].copy()
    size = (32, 32)
    colors = {
        "WALK": (96, 168, 96),
        "LOOK": (168, 168, 96),
        "USE": (168, 120, 96),
        "TALK": (120, 96, 168),
    }
    surface = pygame.Surface(size, pygame.SRCALPHA)
    base_color = colors.get(verb, (200, 200, 200))
    pygame.draw.polygon(
        surface,
        (*base_color, 255),
        [(2, 2), (18, 28), (12, 22), (10, 30), (6, 28), (8, 20), (2, 18)],
    )
    pygame.draw.lines(surface, (0, 0, 0), True, [(2, 2), (18, 28), (12, 22), (10, 30), (6, 28), (8, 20), (2, 18)], 2)
    glyph = get_font("timesnewroman", 14).render(verb[0], True, (0, 0, 0))
    surface.blit(glyph, (20, 8))
    _CURSOR_CACHE[verb] = surface
    return surface.copy()


def create_inventory_icon(label: str, color: pygame.Color) -> pygame.Surface:
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    _draw_icon_background(surface, color)
    font = get_font("timesnewroman", 14)
    text = font.render(label[:3], True, (255, 244, 224))
    outline = font.render(label[:3], True, (20, 12, 12))
    rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(outline, rect.move(1, 1))
    surface.blit(text, rect)
    return surface
