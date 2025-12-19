"""Idle animation system - breathing, blinking, subtle movement when stationary.

Adds life to characters when they're not moving, preventing the "mannequin" look.
"""
from __future__ import annotations

from typing import Dict, List, Tuple
import pygame
import math

from .sprite_config import IDLE_CONFIG, PROPORTIONS

Direction = str
Color = Tuple[int, int, int]


class IdleAnimationGenerator:
    """Generates idle animation frames with breathing and subtle movement.

    Idle animations are longer cycles (8 frames vs 4) with:
    - Chest rising/falling (breathing)
    - Occasional blinks
    - Hair swaying gently
    - Weight shifting
    """

    def __init__(self, config: object = None) -> None:
        self.config = config or IDLE_CONFIG

    def create_idle_frame(
        self,
        base_sprite_generator: callable,
        direction: Direction,
        idle_frame: int,
        size: Tuple[int, int] = None,
    ) -> pygame.Surface:
        """Create a single idle animation frame.

        Args:
            base_sprite_generator: Function(direction, frame=0, size) that creates base sprite
            direction: Facing direction
            idle_frame: Idle frame number (0 to FRAME_COUNT-1)
            size: Sprite size

        Returns:
            Idle animation frame with breathing and subtle movement
        """
        if size is None:
            size = (PROPORTIONS.BASE_WIDTH, PROPORTIONS.BASE_HEIGHT)

        # Start with base sprite (frame 0 = standing pose)
        base_sprite = base_sprite_generator(direction, 0, size)

        # Apply idle modifications
        idle_sprite = self._apply_idle_effects(
            base_sprite,
            direction,
            idle_frame,
            size,
        )

        return idle_sprite

    def _apply_idle_effects(
        self,
        sprite: pygame.Surface,
        direction: Direction,
        frame: int,
        size: Tuple[int, int],
    ) -> pygame.Surface:
        """Apply idle animation effects to sprite."""
        result = pygame.Surface(size, pygame.SRCALPHA)

        # Calculate breathing offset (sine wave)
        breath_cycle = frame / float(self.config.FRAME_COUNT)
        breath_offset = int(
            math.sin(breath_cycle * 2 * math.pi) * self.config.BREATH_AMPLITUDE
        )

        # Draw sprite with breathing offset
        result.blit(sprite, (0, breath_offset))

        # Add blink if on blink frame
        if frame == self.config.BLINK_FRAME:
            result = self._add_blink(result, direction)

        # Add hair sway
        hair_sway = self.config.HAIR_SWAY_FRAMES[frame % len(self.config.HAIR_SWAY_FRAMES)]
        if hair_sway != 0:
            result = self._add_hair_sway(result, direction, hair_sway)

        return result

    def _add_blink(
        self,
        sprite: pygame.Surface,
        direction: Direction,
    ) -> pygame.Surface:
        """Add blink effect (draw closed eyes)."""
        # Make a copy to modify
        result = sprite.copy()

        # Eye positions vary by direction
        eye_positions = self._get_eye_positions(direction, sprite.get_size())

        # Draw closed eyes (horizontal lines)
        for eye_x, eye_y in eye_positions:
            # Draw 2-pixel wide closed eye
            pygame.draw.line(result, (40, 40, 50), (eye_x - 1, eye_y), (eye_x + 1, eye_y), 1)

        return result

    def _get_eye_positions(
        self,
        direction: Direction,
        size: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Get eye positions based on direction and sprite size."""
        w, h = size

        # Scale to current sprite size from base
        scale_x = w / float(PROPORTIONS.BASE_WIDTH)
        scale_y = h / float(PROPORTIONS.BASE_HEIGHT)

        head_y = int((h - PROPORTIONS.HEAD_HEIGHT) * scale_y)

        if direction == "down":
            # Front view - two eyes visible
            return [
                (int(6 * scale_x), int(head_y + 2 * scale_y)),
                (int(9 * scale_x), int(head_y + 2 * scale_y)),
            ]
        elif direction in ["left", "up_left", "down_left"]:
            # Left profile - one eye
            return [(int(5 * scale_x), int(head_y + 2 * scale_y))]
        elif direction in ["right", "up_right", "down_right"]:
            # Right profile - one eye
            return [(int(10 * scale_x), int(head_y + 2 * scale_y))]
        else:
            # Back view - no eyes visible
            return []

    def _add_hair_sway(
        self,
        sprite: pygame.Surface,
        direction: Direction,
        sway_offset: int,
    ) -> pygame.Surface:
        """Add subtle hair swaying."""
        # For now, this is a placeholder
        # In a full implementation, you'd redraw hair pixels with offset
        # This would require access to the original drawing code

        # Simple approach: just return sprite as-is
        # (True hair sway would need sprite regeneration with offset)
        return sprite

    def create_idle_animation_set(
        self,
        base_sprite_generator: callable,
        directions: List[Direction],
        scale: float = 2.5,
    ) -> Dict[Direction, List[pygame.Surface]]:
        """Generate complete idle animation sets for all directions.

        Args:
            base_sprite_generator: Function to generate base sprites
            directions: List of directions to generate
            scale: Final scale factor

        Returns:
            Dictionary mapping directions to idle frame lists
        """
        base_size = (PROPORTIONS.BASE_WIDTH, PROPORTIONS.BASE_HEIGHT)
        scaled_size = (int(base_size[0] * scale), int(base_size[1] * scale))

        animations: Dict[Direction, List[pygame.Surface]] = {}

        for direction in directions:
            frames = []
            for frame in range(self.config.FRAME_COUNT):
                sprite = self.create_idle_frame(
                    base_sprite_generator,
                    direction,
                    frame,
                    base_size,
                )
                scaled = pygame.transform.scale(sprite, scaled_size)
                frames.append(scaled)
            animations[direction] = frames

        return animations


class IdleAnimationController:
    """Controls when to use idle vs walk animations.

    Manages state transitions and frame timing for smooth idle behavior.
    """

    def __init__(self, idle_animations: Dict[Direction, List[pygame.Surface]]) -> None:
        self.idle_animations = idle_animations
        self.current_frame = 0
        self.frame_time = 0.0
        self.is_idle = True

    def update(self, dt: float, is_moving: bool, frame_duration: float = 0.2) -> None:
        """Update idle animation state.

        Args:
            dt: Delta time
            is_moving: Whether character is currently moving
            frame_duration: Time per frame (slower for idle)
        """
        self.is_idle = not is_moving

        if self.is_idle:
            self.frame_time += dt
            if self.frame_time >= frame_duration:
                self.frame_time -= frame_duration
                self.current_frame = (self.current_frame + 1) % IDLE_CONFIG.FRAME_COUNT
        else:
            # Reset idle animation when starting to move
            self.current_frame = 0
            self.frame_time = 0.0

    def get_idle_frame(self, direction: Direction) -> pygame.Surface:
        """Get current idle animation frame for direction."""
        frames = self.idle_animations.get(direction, [])
        if not frames:
            return None

        index = min(self.current_frame, len(frames) - 1)
        return frames[index]


# Integration example for Character class
"""
INTEGRATION EXAMPLE - Modify zombie_quest/characters.py:

from .idle_animation import IdleAnimationGenerator, IdleAnimationController, IDLE_CONFIG

class Character:
    def __init__(self, name, position, animations, speed=60.0):
        # ... existing init ...

        # Add idle animations
        self.idle_animations = None  # Set in subclass
        self.idle_controller = None

    def setup_idle_animations(self, base_generator: callable, scale: float = 2.5):
        '''Setup idle animations for this character.'''
        if IDLE_CONFIG.ENABLED:
            generator = IdleAnimationGenerator()
            directions = ["up", "down", "left", "right"]  # Or 8 directions
            self.idle_animations = generator.create_idle_animation_set(
                base_generator, directions, scale
            )
            self.idle_controller = IdleAnimationController(self.idle_animations)

    def update_animation(self, dt: float, moving: bool) -> None:
        '''Update animation frame (with idle support).'''
        # Update idle controller
        if self.idle_controller:
            self.idle_controller.update(dt, moving, frame_duration=0.2)

        direction = self.animation_state.direction
        frames = self.animations.get(direction, [])

        if not moving and self.idle_controller and self.idle_animations:
            # Use idle animation
            idle_frame = self.idle_controller.get_idle_frame(direction)
            if idle_frame:
                self.current_frame = idle_frame
                self.idle = True
                return

        # Use walk animation (existing code)
        if moving:
            self.animation_state.frame_time += dt
            if self.animation_state.frame_time >= ANIMATION.FRAME_DURATION:
                self.animation_state.frame_time -= ANIMATION.FRAME_DURATION
                self.animation_state.frame_index = (
                    (self.animation_state.frame_index + 1) % len(frames)
                )
        else:
            self.animation_state.frame_index = 0

        if frames:
            index = min(self.animation_state.frame_index, len(frames) - 1)
            self.current_frame = frames[index]
        self.idle = not moving

class Hero(Character):
    def __init__(self, position):
        # ... existing init ...

        # Setup idle animations
        from .sprites import create_detailed_hero_sprite
        self.setup_idle_animations(create_detailed_hero_sprite, scale=2.5)
"""
