"""Sprite configuration - all magic numbers extracted for easy tweaking.

This separates visual design from implementation, allowing artists to tune
proportions, colors, and animation timing without touching render code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class SpriteProportions:
    """Character body proportions as ratios of total sprite height."""
    # Base dimensions
    BASE_WIDTH: int = 16
    BASE_HEIGHT: int = 32

    # Vertical proportions (as pixel offsets from bottom)
    FEET_HEIGHT: int = 4
    LEG_HEIGHT: int = 10
    TORSO_HEIGHT: int = 18
    HEAD_HEIGHT: int = 24
    HAIR_HEIGHT: int = 29

    # Horizontal proportions (from center, in pixels)
    BODY_HALF_WIDTH: int = 5
    LEG_WIDTH: int = 3
    ARM_WIDTH: int = 2
    HEAD_WIDTH: int = 6

    # Detail sizes
    EYE_SIZE: int = 1
    HAND_HEIGHT: int = 2
    BOOT_BUCKLE_SIZE: int = 1


@dataclass(frozen=True)
class HeroColorConfig:
    """Hero character color palette - 80s punk rocker."""
    # Skin tones (3-tone shading)
    SKIN: Color = (255, 210, 180)
    SKIN_SHADOW: Color = (220, 170, 140)
    SKIN_HIGHLIGHT: Color = (255, 235, 215)

    # Big hair - deep purple/violet
    HAIR: Color = (60, 20, 80)
    HAIR_SHADOW: Color = (40, 10, 55)
    HAIR_HIGHLIGHT: Color = (90, 40, 120)

    # Purple leather jacket
    JACKET: Color = (100, 40, 130)
    JACKET_SHADOW: Color = (70, 25, 95)
    JACKET_HIGHLIGHT: Color = (140, 70, 170)
    JACKET_ACCENT: Color = (180, 100, 200)  # Studs/zippers

    # Band t-shirt
    SHIRT: Color = (30, 30, 35)
    SHIRT_DESIGN: Color = (200, 50, 100)  # Neon pink logo

    # Tight jeans
    PANTS: Color = (35, 35, 50)
    PANTS_SHADOW: Color = (25, 25, 35)
    PANTS_HIGHLIGHT: Color = (50, 50, 70)

    # Boots & accessories
    BOOTS: Color = (25, 20, 30)
    BOOTS_BUCKLE: Color = (180, 160, 100)
    EARRING: Color = (255, 215, 0)
    WRISTBAND: Color = (200, 50, 50)


@dataclass(frozen=True)
class AnimationFrameData:
    """Animation frame parameters - walk cycle, bob, swing values."""
    # Walk cycle parameters (4-frame cycle)
    WALK_BOB: List[int] = None  # Vertical head bob
    LEG_PHASE: List[int] = None  # Leg position in walk
    ARM_SWING: List[int] = None  # Arm swing amount
    HAIR_FLOW: List[int] = None  # Hair sway

    # Zombie shamble (more jerky)
    SHAMBLE_Y: List[int] = None
    SHAMBLE_X: List[int] = None
    ARM_HANG: List[int] = None
    LEG_DRAG: List[int] = None

    def __post_init__(self):
        # Use object.__setattr__ for frozen dataclass
        if self.WALK_BOB is None:
            object.__setattr__(self, 'WALK_BOB', [0, -1, 0, -1])
        if self.LEG_PHASE is None:
            object.__setattr__(self, 'LEG_PHASE', [0, 1, 2, 1])
        if self.ARM_SWING is None:
            object.__setattr__(self, 'ARM_SWING', [0, 1, 2, 1])
        if self.HAIR_FLOW is None:
            object.__setattr__(self, 'HAIR_FLOW', [-1, 0, 1, 0])
        if self.SHAMBLE_Y is None:
            object.__setattr__(self, 'SHAMBLE_Y', [0, -1, 1, 0])
        if self.SHAMBLE_X is None:
            object.__setattr__(self, 'SHAMBLE_X', [0, 1, 0, -1])
        if self.ARM_HANG is None:
            object.__setattr__(self, 'ARM_HANG', [1, 2, 2, 1])
        if self.LEG_DRAG is None:
            object.__setattr__(self, 'LEG_DRAG', [0, 1, 2, 1])


@dataclass(frozen=True)
class IdleAnimationConfig:
    """Idle animation configuration - breathing, subtle movement."""
    ENABLED: bool = True
    FRAME_COUNT: int = 8  # Longer cycle for idle
    BREATH_AMPLITUDE: int = 1  # Pixels of vertical movement
    BLINK_FRAME: int = 5  # Which frame to blink on
    HAIR_SWAY_FRAMES: List[int] = None  # Subtle hair movement

    def __post_init__(self):
        if self.HAIR_SWAY_FRAMES is None:
            object.__setattr__(self, 'HAIR_SWAY_FRAMES', [0, 0, 1, 1, 0, 0, -1, -1])


@dataclass(frozen=True)
class ShadowConfig:
    """Drop shadow configuration for all characters."""
    ENABLED: bool = True
    OFFSET_X: int = 2  # Shadow offset from character
    OFFSET_Y: int = 2
    ELLIPSE_WIDTH_RATIO: float = 0.8  # Shadow width vs character width
    ELLIPSE_HEIGHT: int = 6  # Shadow height in pixels
    BASE_ALPHA: int = 80  # Shadow opacity
    BLUR_PASSES: int = 2  # Number of blur passes for soft shadow


@dataclass(frozen=True)
class DiagonalSpriteConfig:
    """Configuration for 8-direction movement."""
    ENABLED: bool = True
    # Diagonal directions blend two cardinal directions
    DIAGONAL_BLEND_RATIO: float = 0.7  # How much to blend vs pick primary
    # Direction priorities for animation
    DIRECTION_MAP: Dict[str, Tuple[str, str]] = None

    def __post_init__(self):
        if self.DIRECTION_MAP is None:
            object.__setattr__(self, 'DIRECTION_MAP', {
                'up_left': ('up', 'left'),
                'up_right': ('up', 'right'),
                'down_left': ('down', 'left'),
                'down_right': ('down', 'right'),
            })


@dataclass(frozen=True)
class ZombieColorPresets:
    """Color presets for different zombie types."""

    @staticmethod
    def get_palette(zombie_type: str) -> Dict[str, Color]:
        """Get color palette for zombie type."""
        palettes = {
            "scene": {
                "skin": (120, 160, 120),
                "skin_shadow": (90, 130, 90),
                "skin_highlight": (150, 190, 150),
                "clothes": (70, 50, 90),
                "clothes_shadow": (50, 35, 65),
                "clothes_highlight": (95, 70, 120),
                "hair": (80, 100, 80),
                "eyes": (200, 255, 180),
                "blood": (100, 60, 60),
            },
            "bouncer": {
                "skin": (110, 150, 110),
                "skin_shadow": (80, 120, 80),
                "skin_highlight": (140, 180, 140),
                "clothes": (25, 25, 35),
                "clothes_shadow": (15, 15, 25),
                "clothes_highlight": (40, 40, 55),
                "hair": (30, 35, 30),
                "eyes": (180, 255, 160),
                "blood": (90, 50, 50),
                "shades": (20, 20, 25),
            },
            "rocker": {
                "skin": (130, 170, 130),
                "skin_shadow": (100, 140, 100),
                "skin_highlight": (160, 200, 160),
                "clothes": (120, 30, 40),
                "clothes_shadow": (85, 20, 30),
                "clothes_highlight": (160, 50, 65),
                "hair": (220, 200, 150),
                "eyes": (220, 255, 200),
                "blood": (110, 70, 70),
            },
            "dj": {
                "skin": (125, 165, 125),
                "skin_shadow": (95, 135, 95),
                "skin_highlight": (155, 195, 155),
                "clothes": (50, 50, 75),
                "clothes_shadow": (35, 35, 55),
                "clothes_highlight": (70, 70, 100),
                "hair": (45, 50, 55),
                "eyes": (190, 255, 170),
                "blood": (95, 55, 55),
                "headphones": (60, 60, 70),
            },
        }
        return palettes.get(zombie_type, palettes["scene"])


# Global config instances
PROPORTIONS = SpriteProportions()
HERO_COLORS = HeroColorConfig()
ANIMATION_FRAMES = AnimationFrameData()
IDLE_CONFIG = IdleAnimationConfig()
SHADOW_CONFIG = ShadowConfig()
DIAGONAL_CONFIG = DiagonalSpriteConfig()
