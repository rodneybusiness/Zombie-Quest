"""Asset management and placeholder art generation for Zombie Quest SCI-style demo."""
from __future__ import annotations

import functools
from typing import Dict, Tuple

import pygame

VGA_WIDTH, VGA_HEIGHT = 320, 200
VGA_SIZE = (VGA_WIDTH, VGA_HEIGHT)

# VGA-inspired palette selections for quick placeholder rendering
VGA_COLORS = {
    "sky": (64, 120, 184),
    "ground": (96, 72, 56),
    "interior": (68, 44, 92),
    "alley": (44, 44, 60),
    "highlight": (220, 220, 180),
    "shadow": (32, 32, 48),
    "ui_bar": (38, 54, 92),
    "ui_accent": (140, 176, 228),
    "inventory_bg": (24, 24, 36),
}

_DIRECTION_COLORS = {
    "down": (68, 120, 216),
    "up": (52, 96, 180),
    "left": (60, 104, 196),
    "right": (76, 132, 236),
}

_ZOMBIE_DIRECTION_COLORS = {
    "down": (68, 140, 68),
    "up": (52, 108, 52),
    "left": (60, 120, 60),
    "right": (88, 160, 88),
}


@functools.lru_cache(maxsize=None)
def get_font(size: int) -> pygame.font.Font:
    pygame.font.init()
    font_name = pygame.font.match_font("timesnewroman", bold=False, italic=False)
    if font_name is None:
        font_name = pygame.font.get_default_font()
    return pygame.font.Font(font_name, size)


def _create_label(surface: pygame.Surface, text: str, color=(255, 255, 255)) -> None:
    font = get_font(16)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(text_surface, rect)


@functools.lru_cache(maxsize=None)
def get_background(name: str) -> pygame.Surface:
    surface = pygame.Surface(VGA_SIZE)
    if name == "street_bg":
        surface.fill(VGA_COLORS["sky"])
        pygame.draw.rect(surface, VGA_COLORS["ground"], (0, 120, VGA_WIDTH, 80))
        pygame.draw.rect(surface, (116, 96, 72), (0, 80, VGA_WIDTH, 40))
        pygame.draw.rect(surface, (180, 160, 120), (20, 50, 100, 90))
        pygame.draw.rect(surface, (156, 132, 92), (130, 40, 80, 100))
        pygame.draw.rect(surface, (140, 90, 70), (240, 60, 60, 80))
    elif name == "diner_bg":
        surface.fill((60, 30, 30))
        pygame.draw.rect(surface, (180, 40, 40), (0, 0, VGA_WIDTH, 40))
        pygame.draw.rect(surface, (90, 20, 20), (0, 40, VGA_WIDTH, 160))
        pygame.draw.rect(surface, (120, 80, 60), (40, 80, 240, 70))
        pygame.draw.rect(surface, (200, 120, 90), (50, 60, 60, 60))
        pygame.draw.rect(surface, (200, 120, 90), (210, 60, 60, 60))
    elif name == "alley_bg":
        surface.fill(VGA_COLORS["alley"])
        pygame.draw.rect(surface, (70, 70, 90), (0, 0, VGA_WIDTH, 80))
        pygame.draw.rect(surface, (50, 50, 70), (0, 80, VGA_WIDTH, 120))
        pygame.draw.rect(surface, (30, 30, 40), (120, 40, 80, 120))
        pygame.draw.rect(surface, (120, 120, 140), (40, 100, 40, 80))
    else:
        surface.fill((50, 50, 70))
    _create_label(surface, name.replace("_", " "))
    return surface.convert()


@functools.lru_cache(maxsize=None)
def get_priority_mask(name: str) -> pygame.Surface:
    surface = pygame.Surface(VGA_SIZE)
    surface.fill((0, 0, 0))
    if name == "street_priority":
        pygame.draw.rect(surface, (255, 255, 255), (30, 70, 60, 80))
        pygame.draw.rect(surface, (255, 255, 255), (250, 80, 50, 70))
    elif name == "diner_priority":
        pygame.draw.rect(surface, (255, 255, 255), (60, 60, 200, 40))
    elif name == "alley_priority":
        pygame.draw.rect(surface, (255, 255, 255), (40, 90, 40, 60))
    return surface.convert()


@functools.lru_cache(maxsize=None)
def get_walk_mask(name: str) -> pygame.Surface:
    surface = pygame.Surface(VGA_SIZE)
    surface.fill((0, 0, 0))
    if name == "street_walk":
        pygame.draw.polygon(surface, (255, 255, 255), [(0, 120), (320, 120), (320, 199), (0, 199)])
        pygame.draw.rect(surface, (0, 0, 0), (0, 120, 40, 80))
    elif name == "diner_walk":
        pygame.draw.polygon(surface, (255, 255, 255), [(0, 130), (320, 130), (320, 199), (0, 199)])
        pygame.draw.rect(surface, (0, 0, 0), (40, 130, 80, 70))
    elif name == "alley_walk":
        pygame.draw.polygon(surface, (255, 255, 255), [(10, 110), (310, 110), (320, 199), (0, 199)])
        pygame.draw.rect(surface, (0, 0, 0), (140, 110, 40, 40))
    else:
        pygame.draw.rect(surface, (255, 255, 255), (0, 100, 320, 100))
    return surface.convert()


def _create_sprite_frame(size: Tuple[int, int], color: Tuple[int, int, int], label: str) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((*color, 255))
    pygame.draw.rect(surface, (0, 0, 0, 255), surface.get_rect(), 1)
    font = get_font(10)
    text_surface = font.render(label, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(text_surface, text_rect)
    return surface


@functools.lru_cache(maxsize=None)
def get_hero_sprites(frame_size: Tuple[int, int] = (32, 64)) -> Dict[str, Dict[str, Tuple[pygame.Surface, ...]]]:
    animations: Dict[str, Dict[str, Tuple[pygame.Surface, ...]]] = {}
    frames_per_state = {
        "idle": 1,
        "walk": 6,
    }
    for state, frame_count in frames_per_state.items():
        animations[state] = {}
        for direction, base_color in _DIRECTION_COLORS.items():
            frames = []
            for index in range(frame_count):
                color = tuple(min(255, c + index * 4) for c in base_color)
                label = f"Hero {direction[:1].upper()} {state[:1].upper()}{index + 1}"
                frames.append(_create_sprite_frame(frame_size, color, label))
            animations[state][direction] = tuple(frames)
    return animations


@functools.lru_cache(maxsize=None)
def get_zombie_sprites(frame_size: Tuple[int, int] = (32, 64)) -> Dict[str, Dict[str, Tuple[pygame.Surface, ...]]]:
    animations: Dict[str, Dict[str, Tuple[pygame.Surface, ...]]] = {}
    frames_per_state = {
        "idle": 1,
        "walk": 6,
    }
    for state, frame_count in frames_per_state.items():
        animations[state] = {}
        for direction, base_color in _ZOMBIE_DIRECTION_COLORS.items():
            frames = []
            for index in range(frame_count):
                color = tuple(min(255, c + index * 2) for c in base_color)
                label = f"Zombie {direction[:1].upper()} {state[:1].upper()}{index + 1}"
                frames.append(_create_sprite_frame(frame_size, color, label))
            animations[state][direction] = tuple(frames)
    return animations


@functools.lru_cache(maxsize=None)
def get_ui_icon(label: str, size: Tuple[int, int] = (24, 24)) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((*VGA_COLORS["ui_accent"], 255))
    pygame.draw.rect(surface, (0, 0, 0, 255), surface.get_rect(), 1)
    font = get_font(12)
    text_surface = font.render(label, True, (10, 20, 40))
    text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(text_surface, text_rect)
    return surface


def build_walkbehind_overlay(background: pygame.Surface, priority_mask: pygame.Surface) -> pygame.Surface:
    overlay = pygame.Surface(background.get_size(), pygame.SRCALPHA)
    width, height = background.get_size()
    bg_pixels = pygame.PixelArray(background)
    mask_pixels = pygame.PixelArray(priority_mask)
    overlay_pixels = pygame.PixelArray(overlay)
    white = priority_mask.map_rgb((255, 255, 255))
    for y in range(height):
        for x in range(width):
            if mask_pixels[x, y] == white:
                overlay_pixels[x, y] = bg_pixels[x, y]
            else:
                overlay_pixels[x, y] = 0
    del bg_pixels
    del mask_pixels
    del overlay_pixels
    overlay.set_colorkey((0, 0, 0))
    return overlay.convert_alpha()
