"""Smart radial context menu for verb selection.

Replaces the verb bar with a right-click radial menu that shows only
valid verbs for the hovered object. Inspired by modern action games.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import pygame

from .config import COLORS
from .rooms import Hotspot
from .ui import Verb
from .sprites import create_verb_icon

Color = Tuple[int, int, int]


class RadialMenuItem:
    """A single item in the radial menu."""

    def __init__(self, verb: Verb, angle: float, radius: float) -> None:
        self.verb = verb
        self.angle = angle  # Radians
        self.radius = radius
        self.hovered = False

        # Calculate position
        self.offset_x = math.cos(angle) * radius
        self.offset_y = math.sin(angle) * radius

        # Create icon
        self.icon = create_verb_icon(verb.value, (28, 28))
        self.icon_size = 28

    def get_world_pos(self, center: Tuple[int, int]) -> Tuple[int, int]:
        """Get world position of this menu item."""
        return (
            int(center[0] + self.offset_x),
            int(center[1] + self.offset_y)
        )

    def contains_point(self, center: Tuple[int, int], point: Tuple[int, int],
                      tolerance: float = 20.0) -> bool:
        """Check if point is within this menu item's area."""
        world_pos = self.get_world_pos(center)
        dx = point[0] - world_pos[0]
        dy = point[1] - world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= tolerance


class RadialMenu:
    """Context-sensitive radial menu for verb selection."""

    def __init__(self) -> None:
        self.active = False
        self.center: Tuple[int, int] = (0, 0)
        self.items: List[RadialMenuItem] = []
        self.hovered_item: Optional[RadialMenuItem] = None
        self.selected_verb: Optional[Verb] = None

        # Animation
        self.scale = 0.0
        self.scale_speed = 8.0  # Scale units per second
        self.target_scale = 1.0

        # Visual config
        self.menu_radius = 60.0
        self.inner_radius = 20.0

    def open(self, position: Tuple[int, int], hotspot: Optional[Hotspot],
            fallback_verbs: Optional[List[Verb]] = None) -> None:
        """Open the radial menu at position with valid verbs for hotspot."""
        self.active = True
        self.center = position
        self.scale = 0.0
        self.selected_verb = None

        # Determine valid verbs
        if hotspot:
            valid_verbs = self._get_valid_verbs_for_hotspot(hotspot)
        else:
            # No hotspot - show movement verb only or fallback
            valid_verbs = fallback_verbs or [Verb.WALK]

        # Create menu items arranged in circle
        self.items = []
        count = len(valid_verbs)

        if count == 0:
            return

        # Start angle at top (-π/2)
        start_angle = -math.pi / 2

        for i, verb in enumerate(valid_verbs):
            if count == 1:
                angle = start_angle
            else:
                # Distribute evenly around circle
                angle = start_angle + (2 * math.pi * i / count)

            item = RadialMenuItem(verb, angle, self.menu_radius)
            self.items.append(item)

    def _get_valid_verbs_for_hotspot(self, hotspot: Hotspot) -> List[Verb]:
        """Get list of valid verbs for a hotspot based on its properties."""
        valid = []

        # Check what verbs have messages defined
        if "look" in hotspot.verbs or "look_default" in hotspot.verbs:
            valid.append(Verb.LOOK)

        if "use" in hotspot.verbs or "use_default" in hotspot.verbs:
            valid.append(Verb.USE)

        if "talk" in hotspot.verbs or "talk_default" in hotspot.verbs or hotspot.talk_target:
            valid.append(Verb.TALK)

        # Always include walk
        if Verb.WALK not in valid:
            valid.append(Verb.WALK)

        return valid

    def close(self) -> None:
        """Close the radial menu."""
        self.active = False
        self.items = []
        self.hovered_item = None

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        """Update menu animation and hover states."""
        if not self.active:
            return

        # Update scale animation
        if self.scale < self.target_scale:
            self.scale = min(self.target_scale, self.scale + self.scale_speed * dt)

        # Update hover states
        self.hovered_item = None
        for item in self.items:
            item.hovered = item.contains_point(self.center, mouse_pos)
            if item.hovered:
                self.hovered_item = item

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[Verb]:
        """Handle click on menu. Returns selected verb or None."""
        if not self.active:
            return None

        # Check if clicking inside menu
        for item in self.items:
            if item.contains_point(self.center, mouse_pos):
                self.selected_verb = item.verb
                self.close()
                return item.verb

        # Clicked outside - close menu
        self.close()
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the radial menu."""
        if not self.active or self.scale < 0.01:
            return

        # Create menu surface with alpha
        menu_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Draw background circle
        bg_radius = int(self.menu_radius * self.scale)
        bg_alpha = int(200 * self.scale)
        pygame.draw.circle(
            menu_surf,
            (*COLORS.UI_DARK, bg_alpha),
            self.center,
            bg_radius
        )

        # Draw border
        border_alpha = int(255 * self.scale)
        pygame.draw.circle(
            menu_surf,
            (*COLORS.UI_BORDER, border_alpha),
            self.center,
            bg_radius,
            2
        )

        # Draw inner circle
        inner_radius = int(self.inner_radius * self.scale)
        pygame.draw.circle(
            menu_surf,
            (*COLORS.DEEP_PURPLE, bg_alpha),
            self.center,
            inner_radius
        )

        # Draw menu items
        for item in self.items:
            self._draw_item(menu_surf, item)

        # Draw center dot
        pygame.draw.circle(
            menu_surf,
            (*COLORS.NEON_GOLD, border_alpha),
            self.center,
            4
        )

        surface.blit(menu_surf, (0, 0))

    def _draw_item(self, surface: pygame.Surface, item: RadialMenuItem) -> None:
        """Draw a single menu item."""
        world_pos = item.get_world_pos(self.center)

        # Scale icon based on menu scale
        scaled_size = int(item.icon_size * self.scale)
        if scaled_size < 2:
            return

        scaled_icon = pygame.transform.smoothscale(item.icon, (scaled_size, scaled_size))

        # Draw background circle
        bg_radius = int(18 * self.scale)
        bg_color = COLORS.HOT_MAGENTA if item.hovered else COLORS.UI_DARK
        bg_alpha = int((255 if item.hovered else 220) * self.scale)

        pygame.draw.circle(
            surface,
            (*bg_color, bg_alpha),
            world_pos,
            bg_radius
        )

        # Draw border
        border_color = COLORS.NEON_GOLD if item.hovered else COLORS.UI_BORDER
        border_alpha = int(255 * self.scale)
        border_width = 2 if item.hovered else 1

        pygame.draw.circle(
            surface,
            (*border_color, border_alpha),
            world_pos,
            bg_radius,
            border_width
        )

        # Draw icon
        icon_alpha = int(255 * self.scale)
        scaled_icon.set_alpha(icon_alpha)
        icon_rect = scaled_icon.get_rect(center=world_pos)
        surface.blit(scaled_icon, icon_rect)

        # Draw label if hovered
        if item.hovered and self.scale > 0.8:
            self._draw_label(surface, item, world_pos)

    def _draw_label(self, surface: pygame.Surface, item: RadialMenuItem,
                   position: Tuple[int, int]) -> None:
        """Draw label for a hovered item."""
        from .resources import load_serif_font

        font = load_serif_font(10)
        label = font.render(item.verb.value.upper(), True, COLORS.UI_TEXT)

        # Position label below icon
        label_pos = (
            position[0] - label.get_width() // 2,
            position[1] + int(25 * self.scale)
        )

        # Draw background
        bg_rect = label.get_rect(topleft=label_pos).inflate(4, 2)
        pygame.draw.rect(surface, (*COLORS.UI_DARK, 200), bg_rect, border_radius=2)

        surface.blit(label, label_pos)


class ContextMenuManager:
    """Manages radial menu integration with game systems."""

    def __init__(self) -> None:
        self.radial_menu = RadialMenu()
        self.enabled = True  # Can be disabled to use traditional verb bar

    def toggle_enabled(self) -> None:
        """Toggle between radial menu and traditional verb bar."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.radial_menu.close()

    def open_at_cursor(self, position: Tuple[int, int],
                      hotspot: Optional[Hotspot]) -> None:
        """Open radial menu at cursor position."""
        if not self.enabled:
            return

        self.radial_menu.open(position, hotspot)

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        """Update radial menu."""
        if self.enabled:
            self.radial_menu.update(dt, mouse_pos)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[Verb]:
        """Handle click. Returns selected verb or None."""
        if not self.enabled or not self.radial_menu.active:
            return None

        return self.radial_menu.handle_click(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw radial menu."""
        if self.enabled:
            self.radial_menu.draw(surface)

    def is_active(self) -> bool:
        """Check if radial menu is currently shown."""
        return self.enabled and self.radial_menu.active

    def close(self) -> None:
        """Close radial menu."""
        self.radial_menu.close()
