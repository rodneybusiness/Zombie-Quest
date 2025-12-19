"""Hotspot highlighting system for interactive objects.

Features:
- Highlights hotspots when mouse hovers
- Shows interaction verb icon near cursor
- Glowing outline for interactable objects
- Smooth fade in/out animations
"""
from __future__ import annotations

import math
from typing import Optional, Tuple

import pygame

from .config import COLORS, ANIMATION
from .rooms import Hotspot
from .ui import Verb
from .sprites import create_verb_icon

Color = Tuple[int, int, int]


class HotspotHighlighter:
    """Manages highlighting of hotspots when hovering."""

    def __init__(self) -> None:
        self.current_hotspot: Optional[Hotspot] = None
        self.highlight_alpha = 0.0
        self.fade_speed = 800.0  # Alpha units per second
        self.glow_time = 0.0

        # Pre-create verb cursor icons (small versions)
        self.verb_cursor_icons = {
            Verb.WALK: create_verb_icon("walk", (20, 20)),
            Verb.LOOK: create_verb_icon("look", (20, 20)),
            Verb.USE: create_verb_icon("use", (20, 20)),
            Verb.TALK: create_verb_icon("talk", (20, 20)),
        }

    def set_hotspot(self, hotspot: Optional[Hotspot]) -> None:
        """Set the currently hovered hotspot."""
        if hotspot != self.current_hotspot:
            self.current_hotspot = hotspot
            # Start fade animation

    def update(self, dt: float) -> None:
        """Update highlight animation."""
        self.glow_time += dt

        if self.current_hotspot:
            # Fade in
            self.highlight_alpha = min(255, self.highlight_alpha + self.fade_speed * dt)
        else:
            # Fade out
            self.highlight_alpha = max(0, self.highlight_alpha - self.fade_speed * dt)

    def draw_highlight(self, surface: pygame.Surface, room_offset: Tuple[int, int] = (0, 0)) -> None:
        """Draw highlight effect on the hovered hotspot."""
        if not self.current_hotspot or self.highlight_alpha < 1:
            return

        # Pulsing glow effect
        pulse = (math.sin(self.glow_time * ANIMATION.GLOW_PULSE_SPEED * 1.5) + 1) / 2
        glow_intensity = 0.6 + pulse * 0.4

        # Calculate highlight rect with room offset
        rect = self.current_hotspot.rect.copy()
        rect.x += room_offset[0]
        rect.y += room_offset[1]

        # Draw multiple glow layers for depth
        for i in range(4):
            expansion = (4 - i) * 3
            glow_rect = rect.inflate(expansion * 2, expansion * 2)

            # Calculate alpha for this layer
            layer_alpha = int(self.highlight_alpha * glow_intensity * 0.3 * (i + 1) / 4)

            # Create glow surface
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

            # Draw glowing rectangle
            pygame.draw.rect(
                glow_surf,
                (*COLORS.NEON_GOLD, layer_alpha),
                glow_rect,
                2 + i
            )

            surface.blit(glow_surf, (0, 0))

        # Draw main highlight border
        border_alpha = int(self.highlight_alpha * glow_intensity)
        pygame.draw.rect(
            surface,
            (*COLORS.NEON_GOLD, border_alpha),
            rect,
            2
        )

        # Draw corner markers for extra clarity
        corner_size = 8
        corner_alpha = int(self.highlight_alpha * 0.8)
        self._draw_corner_markers(surface, rect, corner_size, (*COLORS.CYAN_GLOW, corner_alpha))

    def _draw_corner_markers(self, surface: pygame.Surface, rect: pygame.Rect,
                            size: int, color: Tuple[int, int, int, int]) -> None:
        """Draw corner markers on the highlight rectangle."""
        # Top-left
        pygame.draw.line(surface, color, rect.topleft, (rect.left + size, rect.top), 2)
        pygame.draw.line(surface, color, rect.topleft, (rect.left, rect.top + size), 2)

        # Top-right
        pygame.draw.line(surface, color, rect.topright, (rect.right - size, rect.top), 2)
        pygame.draw.line(surface, color, rect.topright, (rect.right, rect.top + size), 2)

        # Bottom-left
        pygame.draw.line(surface, color, rect.bottomleft, (rect.left + size, rect.bottom), 2)
        pygame.draw.line(surface, color, rect.bottomleft, (rect.left, rect.bottom - size), 2)

        # Bottom-right
        pygame.draw.line(surface, color, rect.bottomright, (rect.right - size, rect.bottom), 2)
        pygame.draw.line(surface, color, rect.bottomright, (rect.right, rect.bottom - size), 2)

    def draw_cursor_icon(self, surface: pygame.Surface, cursor_pos: Tuple[int, int],
                        verb: Verb) -> None:
        """Draw verb icon near cursor when hovering a hotspot."""
        if not self.current_hotspot or self.highlight_alpha < 50:
            return

        icon = self.verb_cursor_icons.get(verb)
        if not icon:
            return

        # Position icon slightly offset from cursor
        offset_x, offset_y = 12, 12
        icon_pos = (cursor_pos[0] + offset_x, cursor_pos[1] + offset_y)

        # Apply alpha to icon
        alpha_icon = icon.copy()
        alpha_icon.set_alpha(int(self.highlight_alpha * 0.9))

        # Draw small background circle for visibility
        bg_radius = 12
        bg_surf = pygame.Surface((bg_radius * 2, bg_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            bg_surf,
            (*COLORS.UI_DARK, int(self.highlight_alpha * 0.7)),
            (bg_radius, bg_radius),
            bg_radius
        )
        pygame.draw.circle(
            bg_surf,
            (*COLORS.UI_BORDER, int(self.highlight_alpha * 0.8)),
            (bg_radius, bg_radius),
            bg_radius,
            1
        )

        surface.blit(bg_surf, (icon_pos[0] - 2, icon_pos[1] - 2))
        surface.blit(alpha_icon, icon_pos)

    def is_highlighting(self) -> bool:
        """Check if currently highlighting a hotspot."""
        return self.current_hotspot is not None and self.highlight_alpha > 0


class InteractionRadius:
    """Draws a radius around interactable objects for accessibility."""

    def __init__(self, radius: float = 30.0, enabled: bool = False) -> None:
        self.radius = radius
        self.enabled = enabled
        self.time = 0.0

    def update(self, dt: float) -> None:
        """Update animation."""
        self.time += dt

    def draw(self, surface: pygame.Surface, hotspots: list,
            room_offset: Tuple[int, int] = (0, 0)) -> None:
        """Draw interaction radius around hotspots."""
        if not self.enabled:
            return

        pulse = (math.sin(self.time * 2) + 1) / 2

        for hotspot in hotspots:
            center = hotspot.rect.center
            center_x = center[0] + room_offset[0]
            center_y = center[1] + room_offset[1]

            # Draw pulsing circle
            radius = int(self.radius + pulse * 5)
            alpha = int(80 + pulse * 40)

            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                circle_surf,
                (*COLORS.CYAN_GLOW, alpha),
                (radius, radius),
                radius,
                2
            )

            surface.blit(
                circle_surf,
                (center_x - radius, center_y - radius)
            )
