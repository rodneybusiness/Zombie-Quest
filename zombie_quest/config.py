"""Game configuration - all magic numbers extracted and centralized."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class DisplayConfig:
    """Display and window settings."""
    ROOM_WIDTH: int = 320
    ROOM_HEIGHT: int = 200
    UI_BAR_HEIGHT: int = 40
    MESSAGE_HEIGHT: int = 36
    SCALE_FACTOR: int = 2  # For modern displays

    @property
    def WINDOW_WIDTH(self) -> int:
        return self.ROOM_WIDTH

    @property
    def WINDOW_HEIGHT(self) -> int:
        return self.ROOM_HEIGHT + self.UI_BAR_HEIGHT + self.MESSAGE_HEIGHT

    @property
    def WINDOW_SIZE(self) -> Tuple[int, int]:
        return (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)


@dataclass(frozen=True)
class GameplayConfig:
    """Core gameplay settings."""
    HERO_SPEED: float = 75.0
    ZOMBIE_SPEED: float = 42.0
    ZOMBIE_DETECTION_RADIUS: float = 90.0
    ZOMBIE_WANDER_INTERVAL: float = 2.5
    ZOMBIE_DAMAGE: int = 1
    HERO_MAX_HEALTH: int = 3
    HERO_INVINCIBILITY_TIME: float = 1.5  # After taking damage
    ARRIVAL_TOLERANCE: float = 2.0


@dataclass(frozen=True)
class AnimationConfig:
    """Animation timing settings."""
    FRAME_DURATION: float = 0.15
    MESSAGE_DISPLAY_TIME: float = 4.0
    TRANSITION_DURATION: float = 0.5
    GLOW_PULSE_SPEED: float = 2.0
    PARTICLE_LIFETIME: float = 1.0


@dataclass(frozen=True)
class AudioConfig:
    """Audio settings."""
    MASTER_VOLUME: float = 0.8
    MUSIC_VOLUME: float = 0.6
    SFX_VOLUME: float = 0.8
    AMBIENT_VOLUME: float = 0.4


@dataclass(frozen=True)
class ColorPalette:
    """Neon Minneapolis color palette."""
    # Primary colors
    DEEP_PURPLE: Color = (30, 10, 60)
    ELECTRIC_VIOLET: Color = (139, 47, 201)
    HOT_MAGENTA: Color = (255, 20, 147)
    CYAN_GLOW: Color = (0, 255, 255)
    NEON_GOLD: Color = (255, 215, 0)
    BONE_WHITE: Color = (240, 234, 224)

    # UI colors
    UI_DARK: Color = (28, 8, 52)
    UI_BORDER: Color = (220, 140, 240)
    UI_TEXT: Color = (240, 230, 250)

    # Health colors
    HEALTH_FULL: Color = (255, 50, 100)
    HEALTH_EMPTY: Color = (60, 20, 40)

    # Verb colors
    VERB_WALK: Color = (70, 160, 220)
    VERB_LOOK: Color = (220, 200, 70)
    VERB_USE: Color = (120, 200, 120)
    VERB_TALK: Color = (220, 120, 160)


# Global config instances
DISPLAY = DisplayConfig()
GAMEPLAY = GameplayConfig()
ANIMATION = AnimationConfig()
AUDIO = AudioConfig()
COLORS = ColorPalette()


# Game state enum
class GameState:
    """Game state machine states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    TRANSITION = "transition"
    GAME_OVER = "game_over"
    CREDITS = "credits"
