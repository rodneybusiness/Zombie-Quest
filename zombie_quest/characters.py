"""Character system with stunning pixel art sprites and enhanced gameplay.

Features:
- Detailed pixel art hero with 80s punk rocker aesthetic
- Multiple zombie types with unique visual traits
- Health system with damage and invincibility frames
- Smooth pathfinding and collision detection
- Full keyboard and mouse control support
- Music response system for zombies
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
from typing import Dict, List, Optional, Tuple

import pygame

from .config import GAMEPLAY, ANIMATION
from .pathfinding import GridPathfinder
from .sprites import create_hero_animations, create_zombie_animations
from .juice import SquashStretch

Direction = str
WorldPos = Tuple[float, float]


class ZombieMusicState(Enum):
    """States zombies can enter when exposed to music."""
    HOSTILE = "hostile"          # Normal behavior, attacks player
    ENTRANCED = "entranced"      # Frozen in place, listening to music
    DANCING = "dancing"          # Swaying rhythmically, harmless
    REMEMBERING = "remembering"  # Brief lucidity, may even help player


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


class Hero(Character):
    """The player character - an 80s punk rocker navigating the zombie-infested scene."""

    def __init__(self, position: WorldPos) -> None:
        # Use detailed pixel art sprites
        animations = create_hero_animations(scale=2.5)
        super().__init__("Frontperson", position, animations, speed=GAMEPLAY.HERO_SPEED)

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

        # Keyboard movement
        self.keyboard_velocity = pygame.Vector2(0, 0)
        self.using_keyboard = False

        # JUICE SYSTEMS for MAXIMUM FEEL
        self.squash_stretch = SquashStretch(max_deform=0.12)  # AMPLIFIED from 0.05
        self.last_direction = pygame.Vector2(0, 1)
        self.last_footstep_frame = -1
        self.footstep_callback: Optional[callable] = None  # Hook for sound/dust emission
        self.current_velocity = pygame.Vector2(0, 0)  # Track for squash/stretch

    def set_destination(self, destination: WorldPos, pathfinder: GridPathfinder) -> None:
        """Set a destination to pathfind to (mouse click movement)."""
        self.using_keyboard = False
        self.pathfinder = pathfinder
        path_points = pathfinder.find_path(tuple(self.position), destination)
        self.path = [pygame.Vector2(point) for point in path_points]

        while self.path and (self.path[0] - self.position).length() <= self.arrival_tolerance:
            self.path.pop(0)

        if self.path:
            self.current_target = self.path.pop(0)
        else:
            self.current_target = None

    def handle_keyboard_input(self, keys_pressed: pygame.key.ScancodeWrapper) -> None:
        """Handle keyboard movement input."""
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

        if dx != 0 or dy != 0:
            self.using_keyboard = True
            self.path = []
            self.current_target = None
            self.keyboard_velocity = pygame.Vector2(dx, dy)
            if self.keyboard_velocity.length() > 0:
                self.keyboard_velocity = self.keyboard_velocity.normalize()
        else:
            self.keyboard_velocity = pygame.Vector2(0, 0)
            if self.using_keyboard:
                self.using_keyboard = False

    def update(self, dt: float, room_bounds: Optional[pygame.Rect] = None,
               walkable_check: Optional[callable] = None) -> None:
        """Update hero position and animation."""
        moving = False

        # Update invincibility
        if self.is_invincible:
            self.invincibility_timer -= dt
            self.flash_timer += dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                self.invincibility_timer = 0

        # Keyboard movement takes priority
        if self.using_keyboard and self.keyboard_velocity.length_squared() > 0:
            new_pos = self.position + self.keyboard_velocity * self.speed * dt

            # Check walkability
            can_move = True
            if walkable_check:
                can_move = walkable_check((new_pos.x, new_pos.y))

            # Clamp to room bounds
            if room_bounds and can_move:
                new_pos.x = max(room_bounds.left + 10, min(room_bounds.right - 10, new_pos.x))
                new_pos.y = max(room_bounds.top + 10, min(room_bounds.bottom - 10, new_pos.y))

            if can_move:
                # Track velocity for juice effects
                actual_movement = new_pos - self.position
                self.current_velocity = actual_movement / max(dt, 0.001)

                # Apply squash/stretch on direction change
                direction_change = actual_movement - self.last_direction
                if direction_change.length() > 0.5:
                    self.squash_stretch.apply_impact(actual_movement, strength=0.8)
                    self.last_direction = actual_movement.copy()

                self.position = new_pos
                self._update_direction(self.keyboard_velocity)
                moving = True

        # Pathfinding movement
        elif self.current_target is not None:
            to_target = self.current_target - self.position
            distance = to_target.length()

            if distance <= self.arrival_tolerance:
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_target = None
            else:
                direction = to_target.normalize()
                step = min(distance, self.speed * dt)
                new_pos = self.position + direction * step

                # Check walkability for pathfinding movement too
                can_move = True
                if walkable_check:
                    can_move = walkable_check((new_pos.x, new_pos.y))

                if can_move:
                    # Track velocity for juice effects
                    actual_movement = new_pos - self.position
                    self.current_velocity = actual_movement / max(dt, 0.001)

                    # Apply squash/stretch on direction change
                    direction_change = actual_movement - self.last_direction
                    if direction_change.length() > 0.5:
                        self.squash_stretch.apply_impact(actual_movement, strength=0.6)
                        self.last_direction = actual_movement.copy()

                    self.position = new_pos
                    self._update_direction(direction)
                    moving = True
                else:
                    # Can't move, clear path
                    self.path = []
                    self.current_target = None

        elif self.path:
            self.current_target = self.path.pop(0)

        # Update squash/stretch
        if not moving:
            self.current_velocity = pygame.Vector2(0, 0)

        # FOOTSTEP SYNC: Check animation frame for footstep emission
        if moving and self.animation_state.frame_index in [1, 3]:
            # Emit footstep on specific animation frames
            if self.last_footstep_frame != self.animation_state.frame_index:
                self.last_footstep_frame = self.animation_state.frame_index
                self.emit_footstep()

        self.update_animation(dt, moving)

    def has_arrived(self) -> bool:
        """Check if hero has arrived at destination."""
        return self.current_target is None and not self.path and not self.using_keyboard

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

    def emit_footstep(self) -> None:
        """Emit footstep effect (sound/dust particles)."""
        if self.footstep_callback:
            self.footstep_callback(self.position, self.current_velocity)

    def set_footstep_callback(self, callback: callable) -> None:
        """Set callback for footstep emission."""
        self.footstep_callback = callback

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw hero with AMPLIFIED invincibility visual and squash/stretch."""
        # Update squash/stretch and get deformation
        scale_x, scale_y = self.squash_stretch.update(1/60.0, self.current_velocity)

        # Get base frame
        frame = self.current_frame
        scale = self.compute_scale(room_height)

        # Apply squash/stretch deformation
        width = max(1, int(frame.get_width() * scale * scale_x))
        height = max(1, int(frame.get_height() * scale * scale_y))
        scaled = pygame.transform.scale(frame, (width, height))

        # AMPLIFIED INVINCIBILITY VISUAL: Color overlay instead of strobe
        if self.is_invincible:
            # Create glowing outline overlay
            glow_intensity = abs((self.flash_timer * 4) % 1.0 - 0.5) * 2  # Smooth pulse

            # Create cyan glow overlay
            glow_surf = pygame.Surface((width + 8, height + 8), pygame.SRCALPHA)
            alpha = int(180 * glow_intensity)

            # Draw multiple glow layers for outline effect
            for i in range(3):
                offset = 2 + i * 2
                glow_color = (100, 200, 255, alpha // (i + 1))
                # Draw scaled sprite with glow tint
                temp_surf = pygame.transform.scale(frame, (width + offset, height + offset))
                temp_overlay = pygame.Surface((width + offset, height + offset), pygame.SRCALPHA)
                temp_overlay.fill(glow_color)
                temp_surf.blit(temp_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                glow_surf.blit(temp_surf, (4 - offset // 2, 4 - offset // 2))

            # Draw main sprite on top of glow
            glow_surf.blit(scaled, (4, 4))

            draw_pos = (int(self.position.x - width // 2 - 4), int(self.position.y - height - 4))
            surface.blit(glow_surf, draw_pos)
            return pygame.Rect(draw_pos, (width + 8, height + 8))

        # Normal drawing with squash/stretch
        draw_pos = (int(self.position.x - width // 2), int(self.position.y - height))
        surface.blit(scaled, draw_pos)
        return pygame.Rect(draw_pos, (width, height))


class Zombie(Character):
    """A zombie enemy with shambling movement and player detection.

    Now features music response system - zombies react to different
    types of music based on their type and the intensity of the music.
    """

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

        # Music response system
        self.music_state: ZombieMusicState = ZombieMusicState.HOSTILE
        self.music_effect_timer: float = 0.0
        self.music_memory_duration: float = 0.0

        # Music preferences by zombie type
        self.music_affinities = self._get_music_affinities()

    def _get_music_affinities(self) -> Dict[str, float]:
        """Get music type affinities for this zombie type.

        Returns dict of music_type -> affinity multiplier (higher = more affected)
        """
        affinities = {
            'scene': {
                'new_wave': 1.5,    # Scene kids love new wave
                'electronic': 1.3,   # Electronic is cool
                'guitar': 0.8,       # Less interested in guitar
                'punk': 1.0,         # Moderate interest
                'ambient': 1.2       # Chill vibes
            },
            'bouncer': {
                'new_wave': 0.5,     # Not into new wave
                'electronic': 0.4,   # Too soft
                'guitar': 1.6,       # Rock and metal
                'punk': 1.8,         # Hardcore all the way
                'ambient': 0.3       # Makes them angry
            },
            'rocker': {
                'new_wave': 0.7,     # Eh
                'electronic': 0.5,   # Not their thing
                'guitar': 2.0,       # THIS IS IT
                'punk': 1.7,         # Hell yeah
                'ambient': 0.6       # Boring
            },
            'dj': {
                'new_wave': 1.4,     # Good beats
                'electronic': 2.0,   # Pure bliss
                'guitar': 0.6,       # Too analog
                'punk': 0.7,         # Too chaotic
                'ambient': 1.5       # They can mix this
            }
        }
        return affinities.get(self.zombie_type, affinities['scene'])

    def respond_to_music(self, music_type: str, intensity: float) -> ZombieMusicState:
        """Calculate zombie response to music.

        Args:
            music_type: Type of music ('guitar', 'electronic', 'new_wave', etc.)
            intensity: Music intensity 0.0-1.0

        Returns:
            New music state for this zombie
        """
        # Get affinity for this music type
        affinity = self.music_affinities.get(music_type, 0.5)

        # Calculate effective intensity
        effective_intensity = intensity * affinity

        # Determine state based on effective intensity
        if effective_intensity < 0.3:
            # Weak effect - still hostile
            return ZombieMusicState.HOSTILE
        elif effective_intensity < 0.6:
            # Moderate effect - entranced (frozen)
            self.music_effect_timer = 3.0 + random.uniform(-0.5, 0.5)
            return ZombieMusicState.ENTRANCED
        elif effective_intensity < 0.9:
            # Strong effect - dancing (harmless, swaying)
            self.music_effect_timer = 5.0 + random.uniform(-1.0, 1.0)
            return ZombieMusicState.DANCING
        else:
            # Overwhelming effect - remembering (brief lucidity)
            self.music_effect_timer = 4.0 + random.uniform(-0.5, 0.5)
            self.music_memory_duration = self.music_effect_timer
            return ZombieMusicState.REMEMBERING

    def apply_music_effect(self, music_type: str, intensity: float) -> None:
        """Apply music effect to this zombie."""
        new_state = self.respond_to_music(music_type, intensity)

        # Only transition if not already in a music state or if new state is stronger
        state_priority = {
            ZombieMusicState.HOSTILE: 0,
            ZombieMusicState.ENTRANCED: 1,
            ZombieMusicState.DANCING: 2,
            ZombieMusicState.REMEMBERING: 3
        }

        current_priority = state_priority[self.music_state]
        new_priority = state_priority[new_state]

        if new_priority > current_priority or self.music_effect_timer <= 0:
            self.music_state = new_state

    def update_music_state(self, dt: float) -> None:
        """Update music effect timer and state."""
        if self.music_effect_timer > 0:
            self.music_effect_timer -= dt

            if self.music_effect_timer <= 0:
                # Effect wore off, return to hostile
                self.music_state = ZombieMusicState.HOSTILE
                self.music_effect_timer = 0.0

    def is_harmless(self) -> bool:
        """Check if zombie is currently harmless due to music."""
        return self.music_state in [
            ZombieMusicState.ENTRANCED,
            ZombieMusicState.DANCING,
            ZombieMusicState.REMEMBERING
        ]

    def update(self, dt: float, hero_position: WorldPos, room_rect: pygame.Rect) -> bool:
        """Update zombie movement. Returns True if zombie touched hero."""
        # Update music state first
        self.update_music_state(dt)

        self.wander_timer -= dt
        self.groan_timer -= dt
        moving = False

        # Check distance to hero
        offset = pygame.Vector2(hero_position) - self.position
        distance_to_hero = offset.length()

        # Music state affects behavior
        if self.music_state == ZombieMusicState.ENTRANCED:
            # Frozen in place, listening
            moving = False
            self.is_chasing = False
        elif self.music_state == ZombieMusicState.DANCING:
            # Swaying in place with slight movement
            if self.wander_timer <= 0:
                self.wander_timer = GAMEPLAY.ZOMBIE_WANDER_INTERVAL * 2
                # Gentle swaying motion
                angle = random.uniform(0, 360)
                self.wander_direction = pygame.Vector2(1, 0).rotate(angle) * 0.3
            moving = True
            self.is_chasing = False
        elif self.music_state == ZombieMusicState.REMEMBERING:
            # Slow, contemplative movement away from player
            if self.wander_timer <= 0:
                self.wander_timer = GAMEPLAY.ZOMBIE_WANDER_INTERVAL
                # Move away from hero slowly
                if distance_to_hero > 0:
                    self.wander_direction = -offset.normalize() * 0.5
                else:
                    self.wander_direction = pygame.Vector2(0, 0)
            moving = True
            self.is_chasing = False
        else:
            # Normal hostile behavior
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

        # Check collision with hero (only if hostile)
        collision_distance = 20  # pixels
        touched_hero = distance_to_hero < collision_distance

        # Only damage if hostile
        return touched_hero and not self.is_harmless()

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
