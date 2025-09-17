from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Optional, Tuple

import pygame

from .pathfinding import GridPathfinder
from .resources import create_directional_animation

Direction = str
WorldPos = Tuple[float, float]


@dataclass
class AnimationState:
    direction: Direction = "down"
    frame_index: int = 0
    frame_time: float = 0.0


class Character:
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
        if motion.length_squared() == 0:
            return
        if abs(motion.x) > abs(motion.y):
            self.animation_state.direction = "right" if motion.x > 0 else "left"
        else:
            self.animation_state.direction = "down" if motion.y > 0 else "up"

    def update_animation(self, dt: float, moving: bool) -> None:
        direction = self.animation_state.direction
        frames = self.animations.get(direction, [])
        if not frames:
            return
        if moving:
            self.animation_state.frame_time += dt
            frame_duration = 0.15
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
        frame = self.current_frame
        scale = self.compute_scale(room_height)
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled = pygame.transform.smoothscale(frame, (width, height))
        draw_pos = (int(self.position.x - width // 2), int(self.position.y - height))
        surface.blit(scaled, draw_pos)
        return pygame.Rect(draw_pos, (width, height))

    def compute_scale(self, room_height: int) -> float:
        min_scale = 0.6
        max_scale = 1.15
        relative = max(0.0, min(1.0, self.position.y / max(1.0, float(room_height))))
        return min_scale + (max_scale - min_scale) * relative

    @property
    def foot_position(self) -> Tuple[float, float]:
        return self.position.x, self.position.y


class Hero(Character):
    def __init__(self, position: WorldPos) -> None:
        animations = create_directional_animation("Hero", (70, 110, 200), (42, 70))
        super().__init__("Hero", position, animations, speed=70.0)
        self.path: List[pygame.Vector2] = []
        self.current_target: Optional[pygame.Vector2] = None
        self.arrival_tolerance: float = 2.0
        self.pathfinder: Optional[GridPathfinder] = None

    def set_destination(self, destination: WorldPos, pathfinder: GridPathfinder) -> None:
        self.pathfinder = pathfinder
        path_points = pathfinder.find_path(tuple(self.position), destination)
        self.path = [pygame.Vector2(point) for point in path_points]
        while self.path and (self.path[0] - self.position).length() <= self.arrival_tolerance:
            self.path.pop(0)
        if self.path:
            self.current_target = self.path.pop(0)
        else:
            self.current_target = None

    def update(self, dt: float) -> None:
        moving = False
        if self.current_target is not None:
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
                self.position += direction * step
                self._update_direction(direction)
                moving = True
        elif self.path:
            self.current_target = self.path.pop(0)
        self.update_animation(dt, moving)

    def has_arrived(self) -> bool:
        return self.current_target is None and not self.path


class Zombie(Character):
    def __init__(self, position: WorldPos) -> None:
        animations = create_directional_animation("Zombie", (120, 180, 120), (40, 64))
        super().__init__("Zombie", position, animations, speed=40.0)
        self.wander_timer: float = 0.0
        self.wander_direction = pygame.Vector2(0, 0)

    def update(self, dt: float, hero_position: WorldPos, room_rect: pygame.Rect) -> None:
        self.wander_timer -= dt
        moving = False
        if self.wander_timer <= 0:
            self.wander_timer = 2.5
            offset = pygame.Vector2(hero_position) - self.position
            if offset.length() < 90:
                self.wander_direction = offset.normalize()
            else:
                angle = random.uniform(0, 360)
                self.wander_direction = pygame.Vector2(1, 0).rotate(angle)
        if self.wander_direction.length_squared() > 0:
            self.position += self.wander_direction * self.speed * dt
            self.position.x = max(room_rect.left + 10, min(room_rect.right - 10, self.position.x))
            self.position.y = max(room_rect.top + 10, min(room_rect.bottom - 10, self.position.y))
            self._update_direction(self.wander_direction)
            moving = True
        self.update_animation(dt, moving)
