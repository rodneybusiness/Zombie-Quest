"""Enhanced character system with improved movement feel.

This is a drop-in replacement for characters.py that integrates the
new movement system with acceleration, momentum, and smooth controls.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Optional, Tuple

import pygame

from .config import GAMEPLAY, ANIMATION
from .pathfinding import GridPathfinder
from .sprites import create_hero_animations, create_zombie_animations
from .movement import EnhancedMovement, MovementConfig, DualMovementController

Direction = str
WorldPos = Tuple[float, float]


@dataclass
class AnimationState:
    """Tracks current animation state."""
    direction: Direction = "down"
    frame_index: int = 0
    frame_time: float = 0.0


class Character:
    """Base class for all characters with sprite animation."""

    def __init__(
        self,
        name: str,
        position: WorldPos,
        animations: Dict[Direction, List[pygame.Surface]],
        speed: float = 60.0,
    ) -> None:
        self.name = name
        self.position = pygame.Vector2(position)
        self.speed = speed
        self.animations = animations
        self.animation_state = AnimationState()
        self.current_frame: pygame.Surface = self.animations[self.animation_state.direction][0]
        self.idle = True

    def _update_direction(self, motion: pygame.Vector2) -> None:
        """Update facing direction based on movement."""
        if motion.length_squared() == 0:
            return
        if abs(motion.x) > abs(motion.y):
            self.animation_state.direction = "right" if motion.x > 0 else "left"
        else:
            self.animation_state.direction = "down" if motion.y > 0 else "up"

    def update_animation(self, dt: float, moving: bool) -> None:
        """Update animation frame based on movement state."""
        direction = self.animation_state.direction
        frames = self.animations.get(direction, [])
        if not frames:
            return

        if moving:
            self.animation_state.frame_time += dt
            frame_duration = ANIMATION.FRAME_DURATION
            if self.animation_state.frame_time >= frame_duration:
                self.animation_state.frame_time -= frame_duration
                self.animation_state.frame_index = (self.animation_state.frame_index + 1) % len(frames)
        else:
            self.animation_state.frame_index = 0
            self.animation_state.frame_time = 0

        index = min(self.animation_state.frame_index, len(frames) - 1)
        self.current_frame = frames[index]
        self.idle = not moving

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw character with perspective scaling."""
        frame = self.current_frame
        scale = self.compute_scale(room_height)
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled = pygame.transform.scale(frame, (width, height))
        draw_pos = (int(self.position.x - width // 2), int(self.position.y - height))
        surface.blit(scaled, draw_pos)
        return pygame.Rect(draw_pos, (width, height))

    def compute_scale(self, room_height: int) -> float:
        """Compute scale based on Y position for depth effect."""
        min_scale = 0.6
        max_scale = 1.15
        relative = max(0.0, min(1.0, self.position.y / max(1.0, float(room_height))))
        return min_scale + (max_scale - min_scale) * relative

    @property
    def foot_position(self) -> Tuple[float, float]:
        """Get the foot position for collision/interaction."""
        return self.position.x, self.position.y

    def get_collision_rect(self, room_height: int) -> pygame.Rect:
        """Get collision rectangle for this character."""
        scale = self.compute_scale(room_height)
        width = int(20 * scale)
        height = int(16 * scale)
        return pygame.Rect(
            int(self.position.x - width // 2),
            int(self.position.y - height),
            width,
            height
        )


class EnhancedHero(Character):
    """Enhanced hero with improved movement feel."""

    def __init__(self, position: WorldPos) -> None:
        # Use detailed pixel art sprites
        animations = create_hero_animations(scale=2.5)
        super().__init__("Frontperson", position, animations, speed=GAMEPLAY.HERO_SPEED)

        # Enhanced movement system
        movement_config = MovementConfig(
            max_speed=GAMEPLAY.HERO_SPEED,
            acceleration_time=0.15,
            deceleration_time=0.1
        )
        self.movement = EnhancedMovement(movement_config)
        self.movement_controller = DualMovementController(self.movement)

        # Pathfinding
        self.path: List[pygame.Vector2] = []
        self.current_target: Optional[pygame.Vector2] = None
        self.arrival_tolerance: float = GAMEPLAY.ARRIVAL_TOLERANCE
        self.pathfinder: Optional[GridPathfinder] = None

        # Health system
        self.max_health: int = GAMEPLAY.HERO_MAX_HEALTH
        self.health: int = self.max_health
        self.invincibility_timer: float = 0.0
        self.is_invincible: bool = False
        self.flash_timer: float = 0.0

    def set_destination(self, destination: WorldPos, pathfinder: GridPathfinder) -> None:
        """Set a destination to pathfind to (mouse click movement)."""
        self.pathfinder = pathfinder
        path_points = pathfinder.find_path(tuple(self.position), destination)
        self.path = [pygame.Vector2(point) for point in path_points]

        # Remove points we've already reached
        while self.path and (self.path[0] - self.position).length() <= self.arrival_tolerance:
            self.path.pop(0)

        if self.path:
            self.current_target = self.path.pop(0)
        else:
            self.current_target = None

    def handle_keyboard_input(self, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """Handle keyboard movement input with smooth acceleration."""
        dx, dy = 0, 0

        # Arrow keys and WASD support
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            dx -= 1
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            dx += 1
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            dy -= 1
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            dy += 1

        # Create input direction vector
        input_direction = pygame.Vector2(dx, dy)

        # Normalize diagonal movement
        if input_direction.length_squared() > 0:
            input_direction = input_direction.normalize()

        # Update movement controller (handles keyboard interruption of pathfinding)
        self.movement_controller.set_keyboard_input(input_direction)

        # Clear pathfinding if keyboard is active
        if input_direction.length_squared() > 0:
            self.path = []
            self.current_target = None

    def update(self, dt: float, room_bounds: Optional[pygame.Rect] = None,
               walkable_check: Optional[callable] = None) -> None:
        """Update hero position with enhanced movement."""
        # Update invincibility
        if self.is_invincible:
            self.invincibility_timer -= dt
            self.flash_timer += dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.invincibility_timer = 0

        # Handle pathfinding if active
        if self.current_target is not None:
            to_target = self.current_target - self.position
            distance = to_target.length()

            if distance <= self.arrival_tolerance:
                # Reached waypoint
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_target = None
                    self.movement_controller.cancel_pathfinding()
            else:
                # Move toward target
                direction = to_target.normalize()
                self.movement_controller.set_pathfinding_direction(direction)
        elif self.path:
            self.current_target = self.path.pop(0)
        else:
            # No pathfinding active
            self.movement_controller.cancel_pathfinding()

        # Update movement system
        velocity, is_moving = self.movement_controller.update(dt)

        # Apply movement with collision checking
        if velocity.length_squared() > 0:
            new_pos = self.position + velocity * dt

            # Check walkability
            can_move = True
            if walkable_check:
                can_move = walkable_check((new_pos.x, new_pos.y))

            # Clamp to room bounds
            if room_bounds and can_move:
                new_pos.x = max(room_bounds.left + 10, min(room_bounds.right - 10, new_pos.x))
                new_pos.y = max(room_bounds.top + 10, min(room_bounds.bottom - 10, new_pos.y))

            if can_move:
                self.position = new_pos
            else:
                # Hit obstacle - stop pathfinding
                if self.current_target:
                    self.path = []
                    self.current_target = None
                    self.movement_controller.cancel_pathfinding()

        # Update facing direction from movement
        if velocity.length_squared() > 0.1:
            cardinal_dir = self.movement.get_cardinal_direction()
            self.animation_state.direction = cardinal_dir

        # Update animation
        self.update_animation(dt, is_moving)

    def has_arrived(self) -> bool:
        """Check if hero has arrived at destination."""
        return self.current_target is None and not self.path and not self.movement.is_moving()

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage. Returns True if hero died."""
        if self.is_invincible:
            return False

        self.health = max(0, self.health - amount)
        self.is_invincible = True
        self.invincibility_timer = GAMEPLAY.HERO_INVINCIBILITY_TIME
        self.flash_timer = 0.0

        return self.health <= 0

    def heal(self, amount: int = 1) -> None:
        """Heal the hero."""
        self.health = min(self.max_health, self.health + amount)

    def is_dead(self) -> bool:
        """Check if hero is dead."""
        return self.health <= 0

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw hero with invincibility flash effect."""
        # Flash when invincible
        if self.is_invincible:
            if int(self.flash_timer * 10) % 2 == 0:
                return pygame.Rect(0, 0, 0, 0)  # Skip frame for flash effect

        return super().draw(surface, room_height)


# Backward compatibility alias
Hero = EnhancedHero


class Zombie(Character):
    """A zombie enemy with shambling movement and player detection."""

    def __init__(self, position: WorldPos, zombie_type: str = "scene") -> None:
        # Use detailed pixel art sprites with type variation
        animations = create_zombie_animations(zombie_type=zombie_type, scale=2.5)
        super().__init__(f"{zombie_type.title()} Zombie", position, animations, speed=GAMEPLAY.ZOMBIE_SPEED)

        self.zombie_type = zombie_type
        self.wander_timer: float = 0.0
        self.wander_direction = pygame.Vector2(0, 0)
        self.detection_radius: float = GAMEPLAY.ZOMBIE_DETECTION_RADIUS
        self.is_chasing: bool = False

        # Groan timer for audio
        self.groan_timer: float = random.uniform(2.0, 5.0)

    def update(self, dt: float, hero_position: WorldPos, room_rect: pygame.Rect) -> bool:
        """Update zombie movement. Returns True if zombie touched hero."""
        self.wander_timer -= dt
        self.groan_timer -= dt
        moving = False

        # Check distance to hero
        offset = pygame.Vector2(hero_position) - self.position
        distance_to_hero = offset.length()

        if self.wander_timer <= 0:
            self.wander_timer = GAMEPLAY.ZOMBIE_WANDER_INTERVAL

            if distance_to_hero < self.detection_radius:
                # Chase the hero
                self.wander_direction = offset.normalize() if distance_to_hero > 0 else pygame.Vector2(0, 0)
                self.is_chasing = True
            else:
                # Random wandering
                angle = random.uniform(0, 360)
                self.wander_direction = pygame.Vector2(1, 0).rotate(angle)
                self.is_chasing = False

        if self.wander_direction.length_squared() > 0:
            self.position += self.wander_direction * self.speed * dt
            self.position.x = max(room_rect.left + 10, min(room_rect.right - 10, self.position.x))
            self.position.y = max(room_rect.top + 10, min(room_rect.bottom - 10, self.position.y))
            self._update_direction(self.wander_direction)
            moving = True

        self.update_animation(dt, moving)

        # Check collision with hero
        collision_distance = 20  # pixels
        return distance_to_hero < collision_distance

    def should_groan(self) -> bool:
        """Check if zombie should make a groan sound."""
        if self.groan_timer <= 0:
            self.groan_timer = random.uniform(3.0, 8.0)
            return True
        return False


class ZombieSpawner:
    """Manages zombie spawning and types for a room."""

    ZOMBIE_TYPES = ["scene", "bouncer", "rocker", "dj"]

    @staticmethod
    def create_zombie(position: WorldPos, room_id: str = "") -> Zombie:
        """Create a zombie with appropriate type for the room."""
        type_by_room = {
            "hennepin_outside": ["bouncer", "scene"],
            "record_store": ["scene", "rocker"],
            "college_station": ["dj", "scene"],
            "backstage_stage": ["rocker", "scene", "bouncer"],
        }

        types = type_by_room.get(room_id, ["scene"])
        zombie_type = random.choice(types)

        return Zombie(position, zombie_type)

    @staticmethod
    def create_zombies_for_room(room_data: List[Dict], room_id: str = "") -> List[Zombie]:
        """Create all zombies for a room from data."""
        zombies = []
        for z_data in room_data:
            position = tuple(z_data.get("position", (160, 120)))
            zombie_type = z_data.get("type", None)

            if zombie_type:
                zombies.append(Zombie(position, zombie_type))
            else:
                zombies.append(ZombieSpawner.create_zombie(position, room_id))

        return zombies
