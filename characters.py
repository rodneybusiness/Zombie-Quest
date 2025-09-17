"""Character classes for the Zombie Quest SCI-inspired engine."""

from __future__ import annotations

from typing import Dict, List, Tuple

import pygame

import assets
from settings import (
    SCALE_MAX_FACTOR,
    SCALE_MAX_Y,
    SCALE_MIN_FACTOR,
    SCALE_MIN_Y,
)

AnimationSet = Dict[str, Dict[str, List[pygame.Surface]]]


class Character:
    def __init__(self, name: str, animations: AnimationSet, position: Tuple[float, float], speed: float = 60.0) -> None:
        self.name = name
        self.animations = animations
        self.position = pygame.Vector2(position)
        self.speed = speed
        self.state = "idle"
        self.direction = "down"
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.16
        self.current_image: pygame.Surface | None = None
        self.current_rect: pygame.Rect | None = None

    def update_animation(self, dt: float, moving: bool) -> None:
        self.state = "walk" if moving else "idle"
        frames = self.animations[self.state][self.direction]
        if moving:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(frames)
        else:
            self.frame_index = 0
            self.frame_timer = 0.0
        self.current_image = frames[self.frame_index]

    def compute_scale(self) -> float:
        ratio = (self.position.y - SCALE_MIN_Y) / float(SCALE_MAX_Y - SCALE_MIN_Y)
        ratio = max(0.0, min(1.0, ratio))
        return SCALE_MIN_FACTOR + (SCALE_MAX_FACTOR - SCALE_MIN_FACTOR) * ratio

    def get_render(self) -> Tuple[pygame.Surface, pygame.Rect]:
        if self.current_image is None:
            self.current_image = self.animations[self.state][self.direction][0]
        scale = self.compute_scale()
        width = max(1, int(self.current_image.get_width() * scale))
        height = max(1, int(self.current_image.get_height() * scale))
        scaled_image = pygame.transform.smoothscale(self.current_image, (width, height))
        rect = scaled_image.get_rect()
        rect.midbottom = (int(self.position.x), int(self.position.y))
        self.current_rect = rect
        return scaled_image, rect

    def draw(self, surface: pygame.Surface) -> pygame.Rect:
        image, rect = self.get_render()
        surface.blit(image, rect)
        return rect

    def set_position(self, position: Tuple[float, float]) -> None:
        self.position.update(position)


class PathCharacter(Character):
    def __init__(self, name: str, animations: AnimationSet, position: Tuple[float, float], speed: float = 60.0) -> None:
        super().__init__(name, animations, position, speed)
        self.path: List[pygame.Vector2] = []

    def set_path(self, points: List[Tuple[float, float]]) -> None:
        self.path = [pygame.Vector2(p) for p in points]

    def clear_path(self) -> None:
        self.path = []

    def _update_direction(self, delta: pygame.Vector2) -> None:
        if abs(delta.x) > abs(delta.y):
            self.direction = "right" if delta.x > 0 else "left"
        else:
            self.direction = "down" if delta.y > 0 else "up"

    def follow_path(self, dt: float) -> bool:
        if not self.path:
            return False
        target = self.path[0]
        delta = target - self.position
        distance = delta.length()
        if distance < 1e-2:
            self.position = target
            self.path.pop(0)
            return bool(self.path)
        self._update_direction(delta)
        move_distance = min(self.speed * dt, distance)
        if distance > 0:
            self.position += delta.normalize() * move_distance
        if move_distance >= distance:
            self.position = target
            self.path.pop(0)
        return bool(self.path)

    def update(self, dt: float) -> None:
        moving = self.follow_path(dt)
        self.update_animation(dt, moving)


class Hero(PathCharacter):
    def __init__(self, position: Tuple[float, float]) -> None:
        animations = assets.load_character_animations("Hero")
        super().__init__("Hero", animations, position, speed=70.0)


class Zombie(PathCharacter):
    def __init__(self, position: Tuple[float, float]) -> None:
        animations = assets.load_character_animations("Zombie")
        super().__init__("Zombie", animations, position, speed=45.0)
        self.repath_timer = 0.0

    def update(self, dt: float, hero_position: Tuple[float, float], pathfinder) -> None:
        self.repath_timer -= dt
        if self.repath_timer <= 0.0:
            self.repath_timer = 1.5
            path = pathfinder.find_path(tuple(self.position), hero_position)
            if path:
                self.set_path(path)
        super().update(dt)
