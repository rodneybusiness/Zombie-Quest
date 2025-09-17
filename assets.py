"""Placeholder asset generation utilities for the Zombie Quest SCI-style engine."""

from __future__ import annotations

import random
from typing import Dict, List

import pygame

from settings import WORLD_WIDTH, WORLD_HEIGHT

_PLACEHOLDER_CACHE: Dict[str, pygame.Surface] = {}
_CHARACTER_CACHE: Dict[str, Dict[str, Dict[str, List[pygame.Surface]]]] = {}
_CURSOR_CACHE: Dict[str, pygame.Surface] = {}
_FONT_CACHE: Dict[str, pygame.font.Font] = {}


def get_font(name: str, size: int) -> pygame.font.Font:
    """Return a cached pygame font object."""
    key = f"{name}-{size}"
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont(name, size)
    return _FONT_CACHE[key]


def _label_surface(surface: pygame.Surface, text: str, font_size: int = 18) -> None:
    font = get_font("timesnewroman", font_size)
    text_surface = font.render(text, True, (255, 255, 255))
    rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(text_surface, rect)


def create_placeholder_background(name: str) -> pygame.Surface:
    """Create a Sierra-inspired placeholder background surface."""
    cache_key = f"background:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    # Create a subtle dithered gradient reminiscent of VGA artwork.
    base_colors = [(20, 32, 60), (36, 60, 96), (56, 88, 120), (84, 120, 156)]
    for y in range(WORLD_HEIGHT):
        band = y * len(base_colors) // WORLD_HEIGHT
        color = base_colors[band]
        for x in range(WORLD_WIDTH):
            jitter = (x + y) % 2 * 6
            surface.set_at((x, y), (min(color[0] + jitter, 255), min(color[1] + jitter, 255), min(color[2] + jitter, 255)))

    # Add architectural silhouettes.
    pygame.draw.rect(surface, (60, 40, 40), pygame.Rect(0, 60, WORLD_WIDTH, 80))
    pygame.draw.rect(surface, (90, 68, 68), pygame.Rect(40, 40, 120, 70))
    pygame.draw.rect(surface, (36, 48, 80), pygame.Rect(200, 30, 100, 110))

    _label_surface(surface, f"{name.title()} Background")
    _PLACEHOLDER_CACHE[cache_key] = surface
    return surface.copy()


def create_priority_mask(name: str) -> pygame.Surface:
    cache_key = f"priority:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    mask = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    mask.fill((0, 0, 0))
    # White regions denote walk-behind areas such as awnings or counters.
    pygame.draw.polygon(mask, (255, 255, 255), [(60, 40), (140, 40), (140, 110), (60, 110)])
    pygame.draw.polygon(mask, (255, 255, 255), [(210, 30), (300, 30), (300, 120), (210, 120)])
    _PLACEHOLDER_CACHE[cache_key] = mask
    return mask.copy()


def create_walkable_mask(name: str) -> pygame.Surface:
    cache_key = f"walkable:{name}"
    if cache_key in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[cache_key].copy()

    mask = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    mask.fill((0, 0, 0))
    path_points = [(0, 120), (WORLD_WIDTH, 120), (WORLD_WIDTH, WORLD_HEIGHT), (0, WORLD_HEIGHT)]
    pygame.draw.polygon(mask, (255, 255, 255), path_points)
    # Add an obstacle in the center to force A* navigation around it.
    pygame.draw.rect(mask, (0, 0, 0), pygame.Rect(150, 140, 20, 40))
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
    return overlay


def _direction_color(direction: str) -> pygame.Color:
    base = {
        "down": (198, 90, 90),
        "up": (90, 136, 198),
        "left": (120, 168, 96),
        "right": (198, 152, 90),
    }[direction]
    jitter = random.randint(-10, 10)
    return pygame.Color(max(min(base[0] + jitter, 255), 0), max(min(base[1] + jitter, 255), 0), max(min(base[2] + jitter, 255), 0))


def load_character_animations(name: str, frame_size=(32, 64), frames_per_direction: int = 4) -> Dict[str, Dict[str, List[pygame.Surface]]]:
    """Return cached placeholder animations for the requested character."""
    if name in _CHARACTER_CACHE:
        return {state: {direction: [frame.copy() for frame in frames] for direction, frames in dirs.items()} for state, dirs in _CHARACTER_CACHE[name].items()}

    font = get_font("arial", 10)
    directions = ["down", "up", "left", "right"]
    animations: Dict[str, Dict[str, List[pygame.Surface]]] = {"walk": {}, "idle": {}}
    for direction in directions:
        frames: List[pygame.Surface] = []
        for i in range(frames_per_direction):
            frame = pygame.Surface(frame_size, pygame.SRCALPHA)
            frame.fill((0, 0, 0, 0))
            body = pygame.Surface((frame_size[0] - 6, frame_size[1] - 6), pygame.SRCALPHA)
            body.fill((*_direction_color(direction), 255))
            frame.blit(body, (3, 3))
            label = f"{name} {direction[:1].upper()} {i+1}"
            text = font.render(label, True, (20, 20, 20))
            text_rect = text.get_rect(center=(frame_size[0] // 2, frame_size[1] // 2))
            frame.blit(text, text_rect)
            frames.append(frame)
        animations["walk"][direction] = frames
        animations["idle"][direction] = [frames[0]]

    _CHARACTER_CACHE[name] = animations
    return load_character_animations(name, frame_size, frames_per_direction)


def create_ui_icon(label: str, size: pygame.Vector2, color: pygame.Color) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    font = get_font("arial", 14)
    text = font.render(label, True, (0, 0, 0))
    rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
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
    surface.fill((*colors.get(verb, (200, 200, 200)), 255))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    font = get_font("arial", 14)
    text = font.render(verb[0], True, (0, 0, 0))
    rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(text, rect)
    _CURSOR_CACHE[verb] = surface
    return surface.copy()


def create_inventory_icon(label: str, color: pygame.Color) -> pygame.Surface:
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    surface.fill((*color, 255))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    font = get_font("arial", 12)
    text = font.render(label[:3], True, (0, 0, 0))
    rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(text, rect)
    return surface
