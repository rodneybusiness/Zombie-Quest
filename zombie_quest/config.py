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
    SCALE_FACTOR: int = 3  # For modern displays - 3x gives 960x828 window

    @property
    def INTERNAL_WIDTH(self) -> int:
        """Internal render width (unscaled)."""
        return self.ROOM_WIDTH

    @property
    def INTERNAL_HEIGHT(self) -> int:
        """Internal render height (unscaled)."""
        return self.ROOM_HEIGHT + self.UI_BAR_HEIGHT + self.MESSAGE_HEIGHT

    @property
    def WINDOW_WIDTH(self) -> int:
        """Actual window width (scaled for modern displays)."""
        return self.ROOM_WIDTH * self.SCALE_FACTOR

    @property
    def WINDOW_HEIGHT(self) -> int:
        """Actual window height (scaled for modern displays)."""
        return (self.ROOM_HEIGHT + self.UI_BAR_HEIGHT + self.MESSAGE_HEIGHT) * self.SCALE_FACTOR

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

    # Infection system
    INFECTION_PER_HIT: float = 15.0  # Infection gained per zombie hit
    INFECTION_DECAY_RATE: float = 2.0  # Infection lost per second (passive)
    INFECTION_MUSIC_REDUCTION: float = 10.0  # Infection reduced when using music items
    INFECTION_TRANSFORMATION_THRESHOLD: float = 100.0  # Full infection = game over
    INFECTION_VISUAL_THRESHOLD: float = 40.0  # When visual effects start
    INFECTION_HIGH_THRESHOLD: float = 70.0  # When effects intensify

    # Zombie alertness
    ZOMBIE_ALERT_RADIUS: float = 120.0  # Zombies within this radius can be alerted
    ZOMBIE_SUSPICIOUS_TIME: float = 3.0  # How long suspicious state lasts
    ZOMBIE_HUNTING_SPEED_MULT: float = 1.3  # Speed multiplier when hunting
    ZOMBIE_FRENZIED_SPEED_MULT: float = 1.6  # Speed multiplier when frenzied
    ZOMBIE_GROUP_DISTANCE: float = 80.0  # Distance for group coordination
    ZOMBIE_FLANKING_ANGLE: float = 120.0  # Angle for flanking attempts (degrees)

    # Checkpoint system
    CHECKPOINT_INFECTION_RESTORE: float = 30.0  # Infection level when respawning
    INTERACTION_RADIUS: float = 40.0  # Radius for interactions


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

    # Infection colors
    INFECTION_LOW: Color = (100, 255, 100)  # Green - safe
    INFECTION_MED: Color = (255, 200, 50)   # Yellow - warning
    INFECTION_HIGH: Color = (255, 100, 50)  # Orange - danger
    INFECTION_CRITICAL: Color = (255, 20, 20)  # Red - critical
    INFECTION_VEIN: Color = (80, 40, 100)   # Purple veins


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
