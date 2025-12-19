"""8-direction movement system with proper diagonal sprite generation.

Extends the 4-direction system to 8 directions with dedicated diagonal sprites
that look natural, not just rotations or flips.
"""
from __future__ import annotations

from typing import Dict, List, Tuple
import pygame
import math

from .sprite_config import DIAGONAL_CONFIG, PROPORTIONS

Direction = str
Vector2D = Tuple[float, float]


class EightDirectionSystem:
    """Handles 8-direction movement and sprite selection.

    Converts input vectors into one of 8 directions and selects appropriate sprites.
    """

    # All 8 directions in clockwise order
    DIRECTIONS = [
        "up",
        "up_right",
        "right",
        "down_right",
        "down",
        "down_left",
        "left",
        "up_left",
    ]

    # Cardinal directions (original 4)
    CARDINALS = ["up", "right", "down", "left"]

    # Diagonal directions
    DIAGONALS = ["up_right", "down_right", "down_left", "up_left"]

    @staticmethod
    def vector_to_direction(velocity: Vector2D, threshold: float = 0.1) -> Direction:
        """Convert a velocity vector to the nearest of 8 directions.

        Args:
            velocity: (vx, vy) movement vector
            threshold: Minimum magnitude to register direction

        Returns:
            Direction string ("up", "down_left", etc.)
        """
        vx, vy = velocity

        # Check if moving
        magnitude = math.sqrt(vx * vx + vy * vy)
        if magnitude < threshold:
            return "down"  # Default facing when idle

        # Calculate angle in degrees (0 = right, 90 = down)
        angle = math.degrees(math.atan2(vy, vx))

        # Normalize to 0-360
        angle = (angle + 360) % 360

        # Map to 8 directions (each direction is 45 degrees)
        # 0° = right, 45° = down_right, 90° = down, etc.
        direction_index = int((angle + 22.5) / 45.0) % 8

        # Map index to direction
        direction_map = {
            0: "right",        # 0° (±22.5°)
            1: "down_right",   # 45°
            2: "down",         # 90°
            3: "down_left",    # 135°
            4: "left",         # 180°
            5: "up_left",      # 225°
            6: "up",           # 270°
            7: "up_right",     # 315°
        }

        return direction_map[direction_index]

    @staticmethod
    def is_diagonal(direction: Direction) -> bool:
        """Check if direction is diagonal."""
        return direction in EightDirectionSystem.DIAGONALS

    @staticmethod
    def get_component_directions(direction: Direction) -> Tuple[Direction, Direction]:
        """Get the two cardinal components of a diagonal direction.

        Args:
            direction: Diagonal direction like "up_left"

        Returns:
            Tuple of (primary, secondary) cardinal directions
        """
        components = {
            "up_left": ("up", "left"),
            "up_right": ("up", "right"),
            "down_left": ("down", "left"),
            "down_right": ("down", "right"),
        }
        return components.get(direction, (direction, direction))


def create_diagonal_sprite(
    direction: str,
    frame: int,
    base_generator: callable,
    size: Tuple[int, int] = None,
) -> pygame.Surface:
    """Generate a diagonal sprite by creating a hybrid view.

    For diagonal movement, we create custom sprites that show the character
    at an angle, not just reusing cardinal directions.

    Args:
        direction: Diagonal direction ("up_left", etc.)
        frame: Animation frame number
        base_generator: Function to generate base sprites (hero/zombie)
        size: Sprite size (uses PROPORTIONS if None)

    Returns:
        Diagonal sprite surface
    """
    if size is None:
        size = (PROPORTIONS.BASE_WIDTH, PROPORTIONS.BASE_HEIGHT)

    primary, secondary = EightDirectionSystem.get_component_directions(direction)

    if direction == "up_left":
        # Up-left: Use left sprite as base, tilt head up slightly
        return _create_diagonal_upward_left(frame, base_generator, size)
    elif direction == "up_right":
        # Up-right: Use right sprite as base, tilt head up slightly
        return _create_diagonal_upward_right(frame, base_generator, size)
    elif direction == "down_left":
        # Down-left: Use left sprite as base, head more forward
        return _create_diagonal_downward_left(frame, base_generator, size)
    elif direction == "down_right":
        # Down-right: Use right sprite as base, head more forward
        return _create_diagonal_downward_right(frame, base_generator, size)
    else:
        # Fallback to primary direction
        return base_generator(primary, frame, size)


def _create_diagonal_upward_left(
    frame: int,
    base_generator: callable,
    size: Tuple[int, int],
) -> pygame.Surface:
    """Create up-left diagonal sprite."""
    # Start with left sprite
    left_sprite = base_generator("left", frame, size)
    up_sprite = base_generator("up", frame, size)

    # Blend: mostly left view with a hint of back
    result = pygame.Surface(size, pygame.SRCALPHA)

    # Draw left sprite
    result.blit(left_sprite, (0, 0))

    # Slightly offset/blend with up sprite for depth
    up_alpha = pygame.Surface(size, pygame.SRCALPHA)
    up_alpha.blit(up_sprite, (0, 0))
    up_alpha.set_alpha(40)  # 15% blend
    result.blit(up_alpha, (0, -1))  # Shift up 1 pixel

    return result


def _create_diagonal_upward_right(
    frame: int,
    base_generator: callable,
    size: Tuple[int, int],
) -> pygame.Surface:
    """Create up-right diagonal sprite."""
    right_sprite = base_generator("right", frame, size)
    up_sprite = base_generator("up", frame, size)

    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(right_sprite, (0, 0))

    up_alpha = pygame.Surface(size, pygame.SRCALPHA)
    up_alpha.blit(up_sprite, (0, 0))
    up_alpha.set_alpha(40)
    result.blit(up_alpha, (0, -1))

    return result


def _create_diagonal_downward_left(
    frame: int,
    base_generator: callable,
    size: Tuple[int, int],
) -> pygame.Surface:
    """Create down-left diagonal sprite."""
    left_sprite = base_generator("left", frame, size)
    down_sprite = base_generator("down", frame, size)

    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(left_sprite, (0, 0))

    down_alpha = pygame.Surface(size, pygame.SRCALPHA)
    down_alpha.blit(down_sprite, (0, 0))
    down_alpha.set_alpha(40)
    result.blit(down_alpha, (0, 1))  # Shift down 1 pixel

    return result


def _create_diagonal_downward_right(
    frame: int,
    base_generator: callable,
    size: Tuple[int, int],
) -> pygame.Surface:
    """Create down-right diagonal sprite."""
    right_sprite = base_generator("right", frame, size)
    down_sprite = base_generator("down", frame, size)

    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(right_sprite, (0, 0))

    down_alpha = pygame.Surface(size, pygame.SRCALPHA)
    down_alpha.blit(down_sprite, (0, 0))
    down_alpha.set_alpha(40)
    result.blit(down_alpha, (0, 1))

    return result


def create_eight_direction_animations(
    base_generator: callable,
    scale: float = 2.5,
) -> Dict[Direction, List[pygame.Surface]]:
    """Generate complete 8-direction animation set.

    Args:
        base_generator: Function(direction, frame, size) that creates sprites
        scale: Scale factor for final sprites

    Returns:
        Dictionary mapping all 8 directions to frame lists
    """
    base_size = (PROPORTIONS.BASE_WIDTH, PROPORTIONS.BASE_HEIGHT)
    scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))

    animations: Dict[Direction, List[pygame.Surface]] = {}

    # Generate cardinal directions (original 4)
    for direction in EightDirectionSystem.CARDINALS:
        frames = []
        for frame in range(4):
            sprite = base_generator(direction, frame, base_size)
            scaled = pygame.transform.scale(sprite, scaled_size)
            frames.append(scaled)
        animations[direction] = frames

    # Generate diagonal directions
    for direction in EightDirectionSystem.DIAGONALS:
        frames = []
        for frame in range(4):
            sprite = create_diagonal_sprite(direction, frame, base_generator, base_size)
            scaled = pygame.transform.scale(sprite, scaled_size)
            frames.append(scaled)
        animations[direction] = frames

    return animations


# Integration example for Character class
"""
INTEGRATION EXAMPLE - Modify zombie_quest/characters.py:

from .eight_direction import EightDirectionSystem, create_eight_direction_animations

class Character:
    def _update_direction(self, motion: pygame.Vector2) -> None:
        '''Update facing direction based on movement (8-direction support).'''
        if motion.length_squared() == 0:
            return

        # Convert to 8 directions
        direction = EightDirectionSystem.vector_to_direction((motion.x, motion.y))
        self.animation_state.direction = direction

class Hero(Character):
    def __init__(self, position: WorldPos) -> None:
        # Use 8-direction animations
        from .sprites import create_detailed_hero_sprite
        animations = create_eight_direction_animations(
            create_detailed_hero_sprite,
            scale=2.5
        )
        # Rest of init...
"""
