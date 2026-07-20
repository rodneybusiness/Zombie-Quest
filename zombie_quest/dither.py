"""Ordered (Bayer) dithering helpers - the Sierra checkerboard idiom.

Sierra's EGA art faked intermediate tones with fixed screen-aligned
patterns, not error diffusion; error diffusion (Floyd-Steinberg) reads as
noise at 320x200. These helpers fill rects and vertical gradients using
2x2 or 4x4 Bayer thresholds between two ZQ-32 ramp shades.
"""
from __future__ import annotations

from typing import Sequence, Tuple

import pygame

Color = Tuple[int, int, int]

BAYER_2X2 = ((0, 2),
             (3, 1))

BAYER_4X4 = ((0, 8, 2, 10),
             (12, 4, 14, 6),
             (3, 11, 1, 9),
             (15, 7, 13, 5))


def dither_fill(surface: pygame.Surface, rect: pygame.Rect,
                dark: Color, light: Color, mix: float,
                matrix: Sequence[Sequence[int]] = BAYER_4X4) -> None:
    """Fill rect with a fixed dark/light pattern; mix 0.0=dark, 1.0=light.

    The pattern is aligned to surface coordinates so adjacent fills tile
    seamlessly, exactly like EGA-era screen-aligned dithers.
    """
    size = len(matrix)
    levels = size * size
    threshold = mix * levels
    for y in range(rect.top, rect.bottom):
        row = matrix[y % size]
        for x in range(rect.left, rect.right):
            surface.set_at((x, y), light if row[x % size] < threshold else dark)


def dither_gradient_vertical(surface: pygame.Surface, rect: pygame.Rect,
                             ramp: Sequence[Color],
                             matrix: Sequence[Sequence[int]] = BAYER_4X4) -> None:
    """Fill rect with a top-to-bottom gradient across a ramp of shades.

    Each adjacent shade pair gets an equal band, blended with the ordered
    pattern - the classic Sierra sky/wall treatment.
    """
    if len(ramp) < 2:
        surface.fill(ramp[0], rect)
        return
    bands = len(ramp) - 1
    height = max(1, rect.height)
    size = len(matrix)
    levels = size * size
    for y in range(rect.top, rect.bottom):
        progress = (y - rect.top) / height * bands
        band = min(bands - 1, int(progress))
        mix = progress - band
        dark, light = ramp[band], ramp[band + 1]
        threshold = mix * levels
        row = matrix[y % size]
        for x in range(rect.left, rect.right):
            surface.set_at((x, y), light if row[x % size] < threshold else dark)


def dim_overlay(size: Tuple[int, int], color: Color = (0, 0, 0),
                coverage: float = 0.5,
                matrix: Sequence[Sequence[int]] = BAYER_2X2) -> pygame.Surface:
    """Palette-safe screen dim: an SRCALPHA surface whose pattern pixels are
    solid `color` and the rest fully transparent. Blitting it darkens
    `coverage` of the pixels without inventing blended colors - used for
    pause/dialog dims instead of alpha fills.
    """
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    pattern_size = len(matrix)
    levels = pattern_size * pattern_size
    threshold = coverage * levels
    for y in range(size[1]):
        row = matrix[y % pattern_size]
        for x in range(size[0]):
            if row[x % pattern_size] < threshold:
                overlay.set_at((x, y), (*color, 255))
    return overlay
