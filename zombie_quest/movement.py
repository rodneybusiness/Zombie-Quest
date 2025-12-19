"""Enhanced movement system with acceleration, momentum, and smooth transitions.

This module provides Hollow Knight/Hades-quality movement feel with:
- Smooth acceleration curves
- Momentum and deceleration
- 8-direction facing with smooth transitions
- Keyboard interruption of pathfinding
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame


@dataclass
class MovementConfig:
    """Configuration for movement feel."""
    max_speed: float = 75.0
    acceleration_time: float = 0.15  # Time to reach max speed
    deceleration_time: float = 0.1   # Time to slide to stop
    min_speed_threshold: float = 5.0  # Below this, snap to zero
    diagonal_compensation: float = 0.707  # sqrt(2)/2 for normalized diagonal

    @property
    def acceleration(self) -> float:
        """Acceleration rate in pixels/sec²."""
        return self.max_speed / self.acceleration_time

    @property
    def deceleration(self) -> float:
        """Deceleration rate in pixels/sec²."""
        return self.max_speed / self.deceleration_time


class EnhancedMovement:
    """Handles smooth character movement with acceleration and momentum."""

    def __init__(self, config: Optional[MovementConfig] = None) -> None:
        self.config = config or MovementConfig()

        # Current velocity
        self.velocity = pygame.Vector2(0, 0)

        # Target velocity (from input)
        self.target_velocity = pygame.Vector2(0, 0)

        # Current facing direction (for 8-way)
        self.facing_direction = pygame.Vector2(0, 1)  # Start facing down
        self.facing_angle = 270.0  # Degrees

    def set_input_direction(self, direction: pygame.Vector2) -> None:
        """Set the desired movement direction from input (should be normalized or zero)."""
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.target_velocity = direction * self.config.max_speed
        else:
            self.target_velocity = pygame.Vector2(0, 0)

    def update(self, dt: float) -> Tuple[pygame.Vector2, bool]:
        """Update velocity with acceleration/deceleration.

        Returns:
            (velocity_vector, is_moving)
        """
        if self.target_velocity.length_squared() > 0:
            # Accelerating toward target
            diff = self.target_velocity - self.velocity
            diff_length = diff.length()

            if diff_length > 0:
                # Apply acceleration
                accel_amount = self.config.acceleration * dt

                if diff_length <= accel_amount:
                    # Snap to target
                    self.velocity = self.target_velocity.copy()
                else:
                    # Accelerate toward target
                    self.velocity += diff.normalize() * accel_amount
        else:
            # Decelerating to stop
            speed = self.velocity.length()

            if speed <= self.config.min_speed_threshold:
                # Snap to zero
                self.velocity = pygame.Vector2(0, 0)
            else:
                # Apply deceleration
                decel_amount = self.config.deceleration * dt

                if speed <= decel_amount:
                    self.velocity = pygame.Vector2(0, 0)
                else:
                    self.velocity -= self.velocity.normalize() * decel_amount

        # Update facing direction
        if self.velocity.length_squared() > self.config.min_speed_threshold ** 2:
            self._update_facing(self.velocity)

        is_moving = self.velocity.length_squared() > 0.1
        return self.velocity, is_moving

    def _update_facing(self, motion: pygame.Vector2) -> None:
        """Update facing direction with 8-way snapping."""
        if motion.length_squared() == 0:
            return

        # Get angle in degrees
        angle = math.degrees(math.atan2(motion.y, motion.x))

        # Snap to 8 directions (0, 45, 90, 135, 180, 225, 270, 315)
        # Adjust so 0° is right, 90° is down, 180° is left, 270° is up
        snapped_angle = round(angle / 45) * 45

        self.facing_angle = snapped_angle
        self.facing_direction = pygame.Vector2(
            math.cos(math.radians(snapped_angle)),
            math.sin(math.radians(snapped_angle))
        )

    def get_cardinal_direction(self) -> str:
        """Get cardinal direction string (down, up, left, right) for animations."""
        angle = self.facing_angle % 360

        # Prioritize left/right for diagonal angles
        if -45 <= angle < 45 or 315 <= angle < 405:
            return "right"
        elif 45 <= angle < 135:
            return "down"
        elif 135 <= angle < 225:
            return "left"
        else:  # 225 <= angle < 315
            return "up"

    def stop_immediately(self) -> None:
        """Stop all movement immediately (for transitions, etc)."""
        self.velocity = pygame.Vector2(0, 0)
        self.target_velocity = pygame.Vector2(0, 0)

    def is_moving(self) -> bool:
        """Check if currently moving."""
        return self.velocity.length_squared() > 0.1


class DualMovementController:
    """Controls movement from both keyboard and pathfinding with smooth transitions."""

    def __init__(self, movement: EnhancedMovement) -> None:
        self.movement = movement
        self.keyboard_active = False
        self.pathfinding_active = False

    def set_keyboard_input(self, direction: pygame.Vector2) -> None:
        """Set keyboard input direction. Non-zero direction cancels pathfinding."""
        if direction.length_squared() > 0:
            # Keyboard takes over
            self.keyboard_active = True
            self.pathfinding_active = False
            self.movement.set_input_direction(direction)
        else:
            self.keyboard_active = False
            if not self.pathfinding_active:
                self.movement.set_input_direction(pygame.Vector2(0, 0))

    def set_pathfinding_direction(self, direction: pygame.Vector2) -> None:
        """Set pathfinding direction. Only applies if keyboard is not active."""
        if not self.keyboard_active:
            self.pathfinding_active = direction.length_squared() > 0
            self.movement.set_input_direction(direction)

    def cancel_pathfinding(self) -> None:
        """Cancel pathfinding movement."""
        self.pathfinding_active = False
        if not self.keyboard_active:
            self.movement.set_input_direction(pygame.Vector2(0, 0))

    def update(self, dt: float) -> Tuple[pygame.Vector2, bool]:
        """Update movement and return (velocity, is_moving)."""
        return self.movement.update(dt)
