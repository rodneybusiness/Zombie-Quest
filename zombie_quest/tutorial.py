"""Non-intrusive tutorial system with contextual hints.

Features:
- Highlights first interactable objects
- Shows control hints that fade after use
- Tracks which hints player has seen
- Contextual tips that appear when relevant
- Can be disabled in settings
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import pygame

from .config import COLORS, ANIMATION
from .resources import load_serif_font

Color = Tuple[int, int, int]


class TutorialHint(Enum):
    """Available tutorial hints."""
    MOVEMENT_WASD = "movement_wasd"
    MOVEMENT_CLICK = "movement_click"
    INTERACT_HOTSPOT = "interact_hotspot"
    VERB_SELECTION = "verb_selection"
    INVENTORY_OPEN = "inventory_open"
    INVENTORY_USE = "inventory_use"
    PAUSE_MENU = "pause_menu"
    ZOMBIE_AVOID = "zombie_avoid"
    HEALTH_LOW = "health_low"
    DIALOGUE_CHOICES = "dialogue_choices"


@dataclass
class HintConfig:
    """Configuration for a tutorial hint."""
    text: str
    duration: float = 5.0  # How long to show (0 = until dismissed)
    auto_dismiss: bool = True  # Auto-dismiss after duration
    position: str = "bottom"  # "top", "bottom", "center", "cursor"
    icon: Optional[str] = None  # Optional icon name


class TutorialSystem:
    """Manages tutorial hints and progression."""

    # Hint definitions
    HINTS: Dict[TutorialHint, HintConfig] = {
        TutorialHint.MOVEMENT_WASD: HintConfig(
            text="Use WASD or Arrow Keys to move",
            duration=4.0,
            position="bottom"
        ),
        TutorialHint.MOVEMENT_CLICK: HintConfig(
            text="Click to move, or use WASD for direct control",
            duration=4.0,
            position="bottom"
        ),
        TutorialHint.INTERACT_HOTSPOT: HintConfig(
            text="Click on objects to interact, or press SPACE when nearby",
            duration=5.0,
            position="bottom"
        ),
        TutorialHint.VERB_SELECTION: HintConfig(
            text="Use number keys 1-4 to select actions, or TAB to cycle",
            duration=4.0,
            position="bottom"
        ),
        TutorialHint.INVENTORY_OPEN: HintConfig(
            text="Press I to open your inventory",
            duration=3.0,
            position="bottom"
        ),
        TutorialHint.INVENTORY_USE: HintConfig(
            text="Select an item, then click an object to use it",
            duration=4.0,
            position="bottom"
        ),
        TutorialHint.PAUSE_MENU: HintConfig(
            text="Press ESC or P to pause",
            duration=3.0,
            position="top"
        ),
        TutorialHint.ZOMBIE_AVOID: HintConfig(
            text="WARNING: Zombies will damage you! Keep your distance!",
            duration=4.0,
            position="center"
        ),
        TutorialHint.HEALTH_LOW: HintConfig(
            text="Your health is low! Find a safe place",
            duration=3.0,
            position="center"
        ),
        TutorialHint.DIALOGUE_CHOICES: HintConfig(
            text="Use arrow keys or mouse to select dialogue options",
            duration=4.0,
            position="bottom"
        ),
    }

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.shown_hints: Set[TutorialHint] = set()
        self.active_hint: Optional[TutorialHint] = None
        self.hint_timer: float = 0.0
        self.hint_alpha: float = 0.0
        self.fade_speed: float = 400.0  # Alpha units per second

        # Tutorial progression
        self.first_movement = False
        self.first_interaction = False
        self.first_inventory_open = False
        self.first_zombie_encounter = False

        # Fonts
        self.font = load_serif_font(13)
        self.icon_font = load_serif_font(16)

    def show_hint(self, hint: TutorialHint, force: bool = False) -> None:
        """Show a tutorial hint (if not already shown)."""
        if not self.enabled:
            return

        # Don't re-show unless forced
        if hint in self.shown_hints and not force:
            return

        # Clear current hint
        if self.active_hint:
            self._dismiss_current()

        # Activate new hint
        self.active_hint = hint
        self.hint_timer = self.HINTS[hint].duration
        self.hint_alpha = 0.0  # Will fade in
        self.shown_hints.add(hint)

    def dismiss_hint(self, hint: TutorialHint) -> None:
        """Manually dismiss a specific hint."""
        if self.active_hint == hint:
            self._dismiss_current()

    def _dismiss_current(self) -> None:
        """Dismiss the current hint."""
        self.active_hint = None
        self.hint_timer = 0.0

    def update(self, dt: float) -> None:
        """Update tutorial state."""
        if not self.enabled or not self.active_hint:
            # Fade out
            self.hint_alpha = max(0.0, self.hint_alpha - self.fade_speed * dt)
            return

        config = self.HINTS[self.active_hint]

        # Fade in
        self.hint_alpha = min(255.0, self.hint_alpha + self.fade_speed * dt)

        # Update timer
        if config.auto_dismiss and config.duration > 0:
            self.hint_timer -= dt
            if self.hint_timer <= 0:
                self._dismiss_current()

    def on_player_moved(self) -> None:
        """Called when player moves for the first time."""
        if not self.first_movement:
            self.first_movement = True
            # Show click-to-move hint after WASD hint
            if TutorialHint.MOVEMENT_WASD in self.shown_hints:
                self.show_hint(TutorialHint.MOVEMENT_CLICK)

    def on_player_interacted(self) -> None:
        """Called when player interacts with a hotspot."""
        if not self.first_interaction:
            self.first_interaction = True
            self.dismiss_hint(TutorialHint.INTERACT_HOTSPOT)

    def on_inventory_opened(self) -> None:
        """Called when player opens inventory."""
        if not self.first_inventory_open:
            self.first_inventory_open = True
            self.dismiss_hint(TutorialHint.INVENTORY_OPEN)
            # Show usage hint
            self.show_hint(TutorialHint.INVENTORY_USE)

    def on_zombie_nearby(self) -> None:
        """Called when zombie gets close to player."""
        if not self.first_zombie_encounter:
            self.first_zombie_encounter = True
            self.show_hint(TutorialHint.ZOMBIE_AVOID)

    def on_health_low(self) -> None:
        """Called when player health is low."""
        self.show_hint(TutorialHint.HEALTH_LOW, force=True)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the current tutorial hint."""
        if not self.enabled or not self.active_hint or self.hint_alpha < 1:
            return

        config = self.HINTS[self.active_hint]
        self._draw_hint(surface, config)

    def _draw_hint(self, surface: pygame.Surface, config: HintConfig) -> None:
        """Draw a tutorial hint."""
        # Render text
        text_surf = self.font.render(config.text, True, COLORS.UI_TEXT)

        # Calculate position
        screen_width, screen_height = surface.get_size()
        padding = 15

        if config.position == "bottom":
            x = (screen_width - text_surf.get_width()) // 2
            y = screen_height - text_surf.get_height() - padding - 50
        elif config.position == "top":
            x = (screen_width - text_surf.get_width()) // 2
            y = padding + 50
        else:  # center
            x = (screen_width - text_surf.get_width()) // 2
            y = (screen_height - text_surf.get_height()) // 2

        # Background
        bg_rect = text_surf.get_rect(topleft=(x - padding, y - padding // 2))
        bg_rect = bg_rect.inflate(padding * 2, padding)

        # Draw background with glow
        self._draw_hint_background(surface, bg_rect)

        # Draw text with alpha
        text_surf.set_alpha(int(self.hint_alpha))
        surface.blit(text_surf, (x, y))

        # Draw dismiss hint
        if config.auto_dismiss and config.duration > 0:
            dismiss_text = f"({int(self.hint_timer)}s)"
            dismiss_surf = self.font.render(dismiss_text, True, (150, 150, 170))
            dismiss_surf.set_alpha(int(self.hint_alpha * 0.7))
            surface.blit(dismiss_surf,
                        (bg_rect.right - dismiss_surf.get_width() - 5, bg_rect.bottom - dismiss_surf.get_height() - 2))

    def _draw_hint_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw hint background with glow."""
        # Glow layers
        for i in range(3):
            glow_rect = rect.inflate(i * 6, i * 6)
            alpha = int((self.hint_alpha * 0.3 * (3 - i) / 3))
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*COLORS.CYAN_GLOW, alpha), glow_rect, border_radius=6)
            surface.blit(glow_surf, (0, 0))

        # Main background
        bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        bg_alpha = int(self.hint_alpha * 0.9)
        pygame.draw.rect(bg_surf, (*COLORS.UI_DARK, bg_alpha), bg_surf.get_rect(), border_radius=6)
        surface.blit(bg_surf, rect.topleft)

        # Border
        border_alpha = int(self.hint_alpha)
        pygame.draw.rect(surface, (*COLORS.CYAN_GLOW, border_alpha), rect, 2, border_radius=6)

    def reset(self) -> None:
        """Reset tutorial progress (for new game)."""
        self.shown_hints.clear()
        self.active_hint = None
        self.first_movement = False
        self.first_interaction = False
        self.first_inventory_open = False
        self.first_zombie_encounter = False


class ObjectHighlighter:
    """Highlights important objects during tutorial."""

    def __init__(self) -> None:
        self.highlighted_objects: List[pygame.Rect] = []
        self.highlight_time = 0.0
        self.enabled = False

    def highlight_object(self, rect: pygame.Rect) -> None:
        """Add an object to highlight."""
        if rect not in self.highlighted_objects:
            self.highlighted_objects.append(rect)
        self.enabled = True

    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.highlighted_objects.clear()
        self.enabled = False

    def update(self, dt: float) -> None:
        """Update highlight animation."""
        if self.enabled:
            self.highlight_time += dt

    def draw(self, surface: pygame.Surface, room_offset: Tuple[int, int] = (0, 0)) -> None:
        """Draw highlights around objects."""
        if not self.enabled or not self.highlighted_objects:
            return

        # Pulsing animation
        pulse = (math.sin(self.highlight_time * ANIMATION.GLOW_PULSE_SPEED * 2) + 1) / 2
        intensity = 0.5 + pulse * 0.5

        for rect in self.highlighted_objects:
            # Offset rect
            draw_rect = rect.copy()
            draw_rect.x += room_offset[0]
            draw_rect.y += room_offset[1]

            # Draw pulsing highlight
            for i in range(4):
                expansion = (4 - i) * 4
                highlight_rect = draw_rect.inflate(expansion * 2, expansion * 2)
                alpha = int(intensity * 80 * (i + 1) / 4)

                glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*COLORS.NEON_GOLD, alpha), highlight_rect, 3 + i)
                surface.blit(glow_surf, (0, 0))

            # Draw arrows pointing to object
            self._draw_pointer_arrows(surface, draw_rect, intensity)

    def _draw_pointer_arrows(self, surface: pygame.Surface, rect: pygame.Rect,
                            intensity: float) -> None:
        """Draw animated arrows pointing at highlighted object."""
        center_x, center_y = rect.center

        # Bounce animation
        bounce = math.sin(self.highlight_time * 4) * 5

        alpha = int(intensity * 255)
        arrow_color = (*COLORS.NEON_GOLD, alpha)

        # Arrow size
        size = 12

        # Top arrow
        points_top = [
            (center_x, rect.top - 15 + bounce),
            (center_x - size // 2, rect.top - 15 - size + bounce),
            (center_x + size // 2, rect.top - 15 - size + bounce),
        ]
        pygame.draw.polygon(surface, arrow_color, points_top)

    def has_highlights(self) -> bool:
        """Check if any objects are highlighted."""
        return len(self.highlighted_objects) > 0
