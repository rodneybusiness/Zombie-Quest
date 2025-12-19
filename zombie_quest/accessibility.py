"""Comprehensive accessibility system for inclusive gameplay.

Features:
- Scalable font sizes (3 levels)
- Colorblind palette swaps (Protanopia, Deuteranopia, Tritanopia)
- Screen shake intensity slider
- Flash effect disable option
- Subtitle system for audio cues
- High contrast mode
- Reduced motion mode
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame

from .config import COLORS
from .resources import load_serif_font

Color = Tuple[int, int, int]


class FontSize(Enum):
    """Font size options."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ColorblindMode(Enum):
    """Colorblind accessibility modes."""
    NONE = "none"
    PROTANOPIA = "protanopia"      # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"      # Blue-blind


@dataclass
class AccessibilityConfig:
    """Complete accessibility configuration."""

    # Font size
    font_size: FontSize = FontSize.MEDIUM

    # Colorblind support
    colorblind_mode: ColorblindMode = ColorblindMode.NONE

    # Screen shake
    screen_shake_intensity: float = 1.0  # 0.0 to 1.0
    screen_shake_enabled: bool = True

    # Flash effects
    flash_effects_enabled: bool = True
    flash_intensity: float = 1.0  # 0.0 to 1.0

    # Subtitles
    subtitles_enabled: bool = True
    subtitle_background: bool = True

    # Visual aids
    high_contrast_mode: bool = False
    reduced_motion: bool = False

    # Interaction
    interaction_radius_visible: bool = False
    hold_to_interact: bool = False  # Hold button instead of press
    hold_duration: float = 0.5  # Seconds

    def get_font_scale(self) -> float:
        """Get font scale multiplier."""
        return {
            FontSize.SMALL: 0.8,
            FontSize.MEDIUM: 1.0,
            FontSize.LARGE: 1.3,
        }[self.font_size]

    def get_scaled_font_size(self, base_size: int) -> int:
        """Get scaled font size."""
        return int(base_size * self.get_font_scale())


class ColorblindPalette:
    """Provides colorblind-friendly color palette swaps."""

    @staticmethod
    def adjust_color(color: Color, mode: ColorblindMode) -> Color:
        """Adjust a color for colorblind mode."""
        if mode == ColorblindMode.NONE:
            return color

        r, g, b = color

        if mode == ColorblindMode.PROTANOPIA:
            # Red-blind: Shift reds toward yellows/greens
            return (
                int(r * 0.567 + g * 0.433),
                int(r * 0.558 + g * 0.442),
                int(b)
            )

        elif mode == ColorblindMode.DEUTERANOPIA:
            # Green-blind: Shift greens toward blues
            return (
                int(r * 0.625 + g * 0.375),
                int(r * 0.7 + g * 0.3),
                int(b)
            )

        elif mode == ColorblindMode.TRITANOPIA:
            # Blue-blind: Shift blues toward greens
            return (
                int(r),
                int(g * 0.95 + b * 0.05),
                int(g * 0.433 + b * 0.567)
            )

        return color

    @staticmethod
    def get_adjusted_palette(mode: ColorblindMode) -> Dict[str, Color]:
        """Get full adjusted color palette."""
        if mode == ColorblindMode.NONE:
            return {
                "primary": COLORS.HOT_MAGENTA,
                "secondary": COLORS.CYAN_GLOW,
                "accent": COLORS.NEON_GOLD,
                "danger": (255, 50, 50),
                "safe": (50, 255, 50),
                "neutral": COLORS.UI_TEXT,
            }

        # Create colorblind-friendly alternatives
        if mode in (ColorblindMode.PROTANOPIA, ColorblindMode.DEUTERANOPIA):
            # Use blue/yellow instead of red/green
            return {
                "primary": (100, 150, 255),  # Blue
                "secondary": (255, 200, 0),  # Yellow
                "accent": (255, 150, 50),    # Orange
                "danger": (255, 100, 0),     # Orange (danger)
                "safe": (100, 150, 255),     # Blue (safe)
                "neutral": COLORS.UI_TEXT,
            }

        else:  # TRITANOPIA
            # Use red/cyan instead of blue/yellow
            return {
                "primary": (255, 100, 100),  # Red
                "secondary": (100, 255, 255),  # Cyan
                "accent": (255, 200, 100),   # Yellow
                "danger": (255, 50, 50),     # Red (danger)
                "safe": (100, 255, 255),     # Cyan (safe)
                "neutral": COLORS.UI_TEXT,
            }


@dataclass
class SubtitleEntry:
    """A single subtitle entry."""
    text: str
    duration: float
    remaining: float
    color: Color = COLORS.UI_TEXT
    speaker: Optional[str] = None


class SubtitleSystem:
    """Manages on-screen subtitles for audio cues and dialogue."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.entries: List[SubtitleEntry] = []
        self.font = load_serif_font(14)
        self.speaker_font = load_serif_font(12)
        self.max_entries = 3

    def add_subtitle(self, text: str, duration: float = 2.0,
                    color: Optional[Color] = None, speaker: Optional[str] = None) -> None:
        """Add a subtitle."""
        if not self.enabled:
            return

        entry = SubtitleEntry(
            text=text,
            duration=duration,
            remaining=duration,
            color=color or COLORS.UI_TEXT,
            speaker=speaker
        )

        self.entries.append(entry)

        # Limit to max entries
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def update(self, dt: float) -> None:
        """Update subtitle timers."""
        remaining_entries = []
        for entry in self.entries:
            entry.remaining -= dt
            if entry.remaining > 0:
                remaining_entries.append(entry)
        self.entries = remaining_entries

    def draw(self, surface: pygame.Surface, config: AccessibilityConfig) -> None:
        """Draw subtitles at bottom of screen."""
        if not self.enabled or not self.entries:
            return

        screen_height = surface.get_height()
        y_offset = screen_height - 60  # Start from bottom

        for entry in reversed(self.entries):  # Newest at bottom
            self._draw_entry(surface, entry, y_offset, config)
            y_offset -= 30  # Move up for next entry

    def _draw_entry(self, surface: pygame.Surface, entry: SubtitleEntry,
                   y: int, config: AccessibilityConfig) -> None:
        """Draw a single subtitle entry."""
        # Scale font
        font_size = config.get_scaled_font_size(14)
        font = load_serif_font(font_size)

        # Render text
        if entry.speaker:
            speaker_text = f"{entry.speaker}: "
            speaker_surf = font.render(speaker_text, True, COLORS.NEON_GOLD)
            message_surf = font.render(entry.text, True, entry.color)

            # Combine
            total_width = speaker_surf.get_width() + message_surf.get_width()
            combined = pygame.Surface((total_width, font_size + 4), pygame.SRCALPHA)
            combined.blit(speaker_surf, (0, 0))
            combined.blit(message_surf, (speaker_surf.get_width(), 0))
            text_surf = combined
        else:
            text_surf = font.render(entry.text, True, entry.color)

        # Position centered
        x = (surface.get_width() - text_surf.get_width()) // 2

        # Background if enabled
        if config.subtitle_background:
            bg_rect = text_surf.get_rect(topleft=(x - 8, y - 4)).inflate(16, 8)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*COLORS.UI_DARK, 220), bg_surf.get_rect(), border_radius=4)
            surface.blit(bg_surf, bg_rect.topleft)

            # Border
            pygame.draw.rect(surface, (*COLORS.UI_BORDER, 180), bg_rect, 1, border_radius=4)

        # Fade out
        fade_time = 0.3
        if entry.remaining < fade_time:
            alpha = int(255 * (entry.remaining / fade_time))
            text_surf.set_alpha(alpha)

        surface.blit(text_surf, (x, y))


class AccessibilityMenu:
    """In-game menu for adjusting accessibility settings."""

    def __init__(self, config: AccessibilityConfig, rect: pygame.Rect) -> None:
        self.config = config
        self.rect = rect
        self.visible = False

        self.font = load_serif_font(12)
        self.title_font = load_serif_font(16)

        self.options = [
            ("Font Size", "font_size"),
            ("Colorblind Mode", "colorblind_mode"),
            ("Screen Shake", "screen_shake"),
            ("Flash Effects", "flash_effects"),
            ("Subtitles", "subtitles"),
            ("High Contrast", "high_contrast"),
            ("Reduced Motion", "reduced_motion"),
            ("Show Interaction Radius", "interaction_radius"),
        ]

        self.selected_index = 0

    def toggle(self) -> None:
        """Toggle menu visibility."""
        self.visible = not self.visible

    def handle_key(self, key: int) -> bool:
        """Handle keyboard input. Returns True if handled."""
        if not self.visible:
            return False

        if key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.options)
            return True
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            return True
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._adjust_option(key == pygame.K_RIGHT)
            return True
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._toggle_option()
            return True
        elif key == pygame.K_ESCAPE:
            self.toggle()
            return True

        return False

    def _adjust_option(self, increase: bool) -> None:
        """Adjust the selected option."""
        option_id = self.options[self.selected_index][1]

        if option_id == "font_size":
            sizes = list(FontSize)
            current_idx = sizes.index(self.config.font_size)
            new_idx = (current_idx + (1 if increase else -1)) % len(sizes)
            self.config.font_size = sizes[new_idx]

        elif option_id == "colorblind_mode":
            modes = list(ColorblindMode)
            current_idx = modes.index(self.config.colorblind_mode)
            new_idx = (current_idx + (1 if increase else -1)) % len(modes)
            self.config.colorblind_mode = modes[new_idx]

        elif option_id == "screen_shake":
            self.config.screen_shake_intensity = max(0.0, min(1.0,
                self.config.screen_shake_intensity + (0.1 if increase else -0.1)))

        elif option_id == "flash_effects":
            self.config.flash_intensity = max(0.0, min(1.0,
                self.config.flash_intensity + (0.1 if increase else -0.1)))

    def _toggle_option(self) -> None:
        """Toggle a boolean option."""
        option_id = self.options[self.selected_index][1]

        if option_id == "subtitles":
            self.config.subtitles_enabled = not self.config.subtitles_enabled
        elif option_id == "high_contrast":
            self.config.high_contrast_mode = not self.config.high_contrast_mode
        elif option_id == "reduced_motion":
            self.config.reduced_motion = not self.config.reduced_motion
        elif option_id == "interaction_radius":
            self.config.interaction_radius_visible = not self.config.interaction_radius_visible

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the accessibility menu."""
        if not self.visible:
            return

        # Background overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Menu box
        menu_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surf, COLORS.UI_DARK, menu_surf.get_rect(), border_radius=8)
        pygame.draw.rect(menu_surf, COLORS.UI_BORDER, menu_surf.get_rect(), 2, border_radius=8)

        # Title
        title = self.title_font.render("ACCESSIBILITY", True, COLORS.HOT_MAGENTA)
        menu_surf.blit(title, (self.rect.width // 2 - title.get_width() // 2, 10))

        # Options
        y_offset = 45
        for i, (label, option_id) in enumerate(self.options):
            color = COLORS.NEON_GOLD if i == self.selected_index else COLORS.UI_TEXT

            # Label
            label_surf = self.font.render(label, True, color)
            menu_surf.blit(label_surf, (20, y_offset))

            # Value
            value_text = self._get_option_value_text(option_id)
            value_surf = self.font.render(value_text, True, color)
            menu_surf.blit(value_surf, (self.rect.width - value_surf.get_width() - 20, y_offset))

            # Selection indicator
            if i == self.selected_index:
                pygame.draw.polygon(menu_surf, COLORS.NEON_GOLD, [
                    (10, y_offset + 5),
                    (15, y_offset + 2),
                    (15, y_offset + 8),
                ])

            y_offset += 30

        # Instructions
        instructions = self.font.render("Arrows: Navigate | Enter/Space: Toggle | Esc: Close", True, (120, 120, 140))
        menu_surf.blit(instructions, (self.rect.width // 2 - instructions.get_width() // 2, self.rect.height - 25))

        surface.blit(menu_surf, self.rect.topleft)

    def _get_option_value_text(self, option_id: str) -> str:
        """Get display text for option value."""
        if option_id == "font_size":
            return self.config.font_size.value.upper()
        elif option_id == "colorblind_mode":
            return self.config.colorblind_mode.value.upper()
        elif option_id == "screen_shake":
            if not self.config.screen_shake_enabled:
                return "OFF"
            return f"{int(self.config.screen_shake_intensity * 100)}%"
        elif option_id == "flash_effects":
            if not self.config.flash_effects_enabled:
                return "OFF"
            return f"{int(self.config.flash_intensity * 100)}%"
        elif option_id == "subtitles":
            return "ON" if self.config.subtitles_enabled else "OFF"
        elif option_id == "high_contrast":
            return "ON" if self.config.high_contrast_mode else "OFF"
        elif option_id == "reduced_motion":
            return "ON" if self.config.reduced_motion else "OFF"
        elif option_id == "interaction_radius":
            return "ON" if self.config.interaction_radius_visible else "OFF"
        return "???"
