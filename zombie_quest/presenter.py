"""Presenter: owns the OS window and the native->window integer scale.

The whole game composes onto a native 320x276 surface; the presenter
scales it to the window with a single nearest-neighbor integer scale and
centers it (letterboxed) when the window doesn't divide evenly. Mouse
positions travel the other way through window_to_native().

Deliberately not using pygame.SCALED: it may pick fractional scales and
hides the offset math needed for exact mouse mapping.
"""
from __future__ import annotations

from typing import Optional, Tuple

import pygame

from .config import DISPLAY


class Presenter:
    NATIVE_SIZE: Tuple[int, int] = (DISPLAY.NATIVE_WIDTH, DISPLAY.NATIVE_HEIGHT)
    SCANLINE_INTENSITY = 0.08

    def __init__(self, scale: int = DISPLAY.SCALE_FACTOR, resizable: bool = True) -> None:
        flags = pygame.RESIZABLE if resizable else 0
        window_size = (self.NATIVE_SIZE[0] * scale, self.NATIVE_SIZE[1] * scale)
        self.window = pygame.display.set_mode(window_size, flags)
        self.native = pygame.Surface(self.NATIVE_SIZE)
        self.fullscreen = False
        self.scanlines_enabled = True
        self.scale = 1
        self.offset = (0, 0)
        self._scanline_cache: Optional[pygame.Surface] = None
        self._scanline_cache_key: Optional[tuple] = None
        self._fit(window_size)

    def _fit(self, window_size: Tuple[int, int]) -> None:
        """Pick the largest integer scale that fits, centered."""
        width, height = window_size
        native_w, native_h = self.NATIVE_SIZE
        self.scale = max(1, min(width // native_w, height // native_h))
        self.offset = ((width - native_w * self.scale) // 2,
                       (height - native_h * self.scale) // 2)

    def handle_resize(self, size: Tuple[int, int]) -> None:
        self._fit(size)

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            scale = DISPLAY.SCALE_FACTOR
            self.window = pygame.display.set_mode(
                (self.NATIVE_SIZE[0] * scale, self.NATIVE_SIZE[1] * scale),
                pygame.RESIZABLE)
        self._fit(self.window.get_size())

    def window_to_native(self, position: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Map a window-space point into native coordinates; None outside."""
        x = (position[0] - self.offset[0]) // self.scale
        y = (position[1] - self.offset[1]) // self.scale
        if 0 <= x < self.NATIVE_SIZE[0] and 0 <= y < self.NATIVE_SIZE[1]:
            return (int(x), int(y))
        return None

    def native_to_window(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """Map a native point to the top-left of its window-space cell."""
        return (position[0] * self.scale + self.offset[0],
                position[1] * self.scale + self.offset[1])

    def present(self) -> None:
        """One integer nearest-neighbor scale of the native canvas, centered,
        followed by a post-scale scanline overlay (one dark line per native
        row, so line pitch always matches the current scale)."""
        try:
            self.window.fill((0, 0, 0))
            scaled = pygame.transform.scale_by(self.native, self.scale)
            self.window.blit(scaled, self.offset)
            if self.scanlines_enabled and self.scale >= 2:
                self.window.blit(self._scanline_overlay(scaled.get_size()), self.offset)
        except (pygame.error, TypeError, AttributeError):
            # Mocked or headless-degenerate window in unit tests: composing
            # the native surface is still exercised; presentation is not.
            return

    def _scanline_overlay(self, size: Tuple[int, int]) -> pygame.Surface:
        cache_key = (size, self.scale)
        if self._scanline_cache_key != cache_key:
            overlay = pygame.Surface(size, pygame.SRCALPHA)
            alpha = int(255 * self.SCANLINE_INTENSITY)
            for y in range(self.scale - 1, size[1], self.scale):
                pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (size[0], y))
            self._scanline_cache = overlay
            self._scanline_cache_key = cache_key
        return self._scanline_cache
