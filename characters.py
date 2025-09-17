"""Character and animation logic for Zombie Quest."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

import assets
from pathfinding import AStarPathfinder

Vector2 = Tuple[float, float]


class SpriteAnimator:
    def __init__(self, animations: Dict[str, Dict[str, Tuple[pygame.Surface, ...]]], frame_duration: float = 0.12) -> None:
        self.animations = animations
        self.frame_duration = frame_duration
        self.state = "idle"
        self.direction = "down"
        self.current_time = 0.0
        self.frame_index = 0

    def set_state(self, state: str) -> None:
        if state != self.state:
            self.state = state
            self.frame_index = 0
            self.current_time = 0.0

    def set_direction(self, direction: str) -> None:
        if direction != self.direction:
            self.direction = direction
            self.frame_index = 0
            self.current_time = 0.0

    def update(self, dt: float) -> None:
        frames = self.animations[self.state][self.direction]
        if len(frames) <= 1:
            return
        self.current_time += dt
        while self.current_time >= self.frame_duration:
            self.current_time -= self.frame_duration
            self.frame_index = (self.frame_index + 1) % len(frames)

    def current_frame(self) -> pygame.Surface:
        return self.animations[self.state][self.direction][self.frame_index]


@dataclass
class Character:
    position: pygame.math.Vector2
    animator: SpriteAnimator
    speed: float
    min_scale: float = 0.7
    max_scale: float = 1.2

    def draw(self, surface: pygame.Surface, scale: float) -> pygame.Rect:
        frame = self.animator.current_frame()
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled_size = (width, height)
        scaled_surface = pygame.transform.smoothscale(frame, scaled_size)
        rect = scaled_surface.get_rect()
        rect.centerx = int(self.position.x)
        rect.bottom = int(self.position.y)
        surface.blit(scaled_surface, rect)
        return rect


class Hero(Character):
    def __init__(self, position: Vector2) -> None:
        animator = SpriteAnimator(assets.get_hero_sprites())
        super().__init__(pygame.math.Vector2(position), animator, speed=70.0)
        self.path: List[Vector2] = []
        self.target_point: Optional[Vector2] = None

    def set_path(self, path: List[Vector2]) -> None:
        self.path = list(path)
        self.target_point = self.path[0] if self.path else None
        if self.path:
            self.animator.set_state("walk")
        else:
            self.animator.set_state("idle")

    def set_destination(self, destination: Vector2, pathfinder: AStarPathfinder) -> None:
        path = pathfinder.find_path((self.position.x, self.position.y), destination)
        if path:
            last = pygame.math.Vector2(path[-1])
            dest_vec = pygame.math.Vector2(destination)
            if last.distance_to(dest_vec) > 4:
                path.append(destination)
        self.set_path(path)

    def update(self, dt: float) -> None:
        if self.path:
            target = pygame.math.Vector2(self.path[0])
            direction_vector = target - self.position
            distance = direction_vector.length()
            if distance <= 1.0:
                self.position = target
                self.path.pop(0)
                if not self.path:
                    self.animator.set_state("idle")
                    self.target_point = None
                else:
                    self.target_point = self.path[0]
                direction_vector = pygame.math.Vector2()
            else:
                direction_vector.normalize_ip()
                self.position += direction_vector * self.speed * dt

            if direction_vector.length_squared() > 0:
                self._update_direction(direction_vector)
                self.animator.set_state("walk")
        else:
            self.animator.set_state("idle")
        self.animator.update(dt)

    def _update_direction(self, vector: pygame.math.Vector2) -> None:
        if abs(vector.x) > abs(vector.y):
            self.animator.set_direction("left" if vector.x < 0 else "right")
        else:
            self.animator.set_direction("up" if vector.y < 0 else "down")

    def has_reached(self, point: Vector2, threshold: float = 6.0) -> bool:
        return self.position.distance_to(pygame.math.Vector2(point)) <= threshold


class Zombie(Character):
    def __init__(self, position: Vector2, patrol_points: Optional[List[Vector2]] = None) -> None:
        animator = SpriteAnimator(assets.get_zombie_sprites(), frame_duration=0.16)
        super().__init__(pygame.math.Vector2(position), animator, speed=40.0, min_scale=0.65, max_scale=1.05)
        self.patrol_points = [pygame.math.Vector2(p) for p in patrol_points] if patrol_points else []
        self.current_patrol_index = 0
        self.path: List[Vector2] = []

    def update(self, dt: float, hero_pos: Vector2, pathfinder: AStarPathfinder) -> None:
        hero_vector = pygame.math.Vector2(hero_pos)
        distance_to_hero = self.position.distance_to(hero_vector)
        target: Optional[Vector2] = None
        if distance_to_hero < 80:
            target = hero_pos
        elif self.patrol_points:
            patrol_target = self.patrol_points[self.current_patrol_index]
            if self.position.distance_to(patrol_target) < 4:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
                patrol_target = self.patrol_points[self.current_patrol_index]
            target = (patrol_target.x, patrol_target.y)

        if target is not None and not self.path:
            self.path = pathfinder.find_path((self.position.x, self.position.y), target)

        if self.path:
            next_point = pygame.math.Vector2(self.path[0])
            direction_vector = next_point - self.position
            distance = direction_vector.length()
            if distance <= 1.0:
                self.position = next_point
                self.path.pop(0)
                direction_vector = pygame.math.Vector2()
            else:
                direction_vector.normalize_ip()
                self.position += direction_vector * self.speed * dt

            if direction_vector.length_squared() > 0:
                self._update_direction(direction_vector)
                self.animator.set_state("walk")
        else:
            self.animator.set_state("idle")
        self.animator.update(dt)

    def _update_direction(self, vector: pygame.math.Vector2) -> None:
        if abs(vector.x) > abs(vector.y):
            self.animator.set_direction("left" if vector.x < 0 else "right")
        else:
            self.animator.set_direction("up" if vector.y < 0 else "down")
