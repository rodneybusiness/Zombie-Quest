"""Room and hotspot definitions for Zombie Quest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

import pygame

import assets
from characters import Hero, Zombie
from pathfinding import PathFinder
from settings import WORLD_HEIGHT, WORLD_WIDTH


@dataclass
class HotspotAction:
    text: str = ""
    requires_item: Optional[str] = None
    success_text: Optional[str] = None
    failure_text: Optional[str] = None
    gives_item: Optional[str] = None
    consumes_item: bool = False
    change_room: Optional[str] = None
    set_state: Dict[str, bool] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)
    once: bool = False
    arrival_position: Optional[Tuple[float, float]] = None


@dataclass
class Hotspot:
    name: str
    rect: pygame.Rect
    actions: Dict[str, HotspotAction] = field(default_factory=dict)
    state: Dict[str, bool] = field(default_factory=dict)
    approach_points: List[pygame.Vector2] = field(default_factory=list)

    def action_for(self, verb: str) -> Optional[HotspotAction]:
        return self.actions.get(verb.upper())

    def best_approach(self, reference: pygame.Vector2) -> pygame.Vector2:
        if not self.approach_points:
            return pygame.Vector2(self.rect.center)
        best = min(self.approach_points, key=lambda point: point.distance_to(reference))
        return best.copy()

    def update_state(self, updates: Dict[str, bool]) -> None:
        for key, value in updates.items():
            self.state[key] = value


class AmbientEffect:
    layer: str = "background"

    def update(self, dt: float) -> None:  # pragma: no cover - animation logic
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:  # pragma: no cover - animation logic
        raise NotImplementedError


class NeonAmbient(AmbientEffect):
    def __init__(self, rect: pygame.Rect, label: str, palette: Iterable[Tuple[int, int, int]], speed: float = 1.0) -> None:
        self.rect = rect
        colors = list(palette)
        if not colors:
            colors = [(220, 80, 120), (240, 180, 160), (140, 220, 220)]
        self.frames = assets.create_neon_frames(label, rect.size, colors)
        self.timer = 0.0
        self.frame = 0
        self.speed = max(0.1, speed)
        self.layer = "background"

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0.0
            self.frame = (self.frame + 1) % len(self.frames)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.frames[self.frame], self.rect)


class RainAmbient(AmbientEffect):
    def __init__(self, speed: float, density: float) -> None:
        self.layer = "overlay"
        height = WORLD_HEIGHT * 2
        self.texture = assets.create_rain_texture("storm", (WORLD_WIDTH, height), density)
        self.speed = speed
        self.offset = 0.0

    def update(self, dt: float) -> None:
        self.offset = (self.offset + self.speed * dt) % self.texture.get_height()

    def draw(self, surface: pygame.Surface) -> None:
        offset_int = int(self.offset)
        h = self.texture.get_height()
        surface.blit(self.texture, (0, -h + offset_int))
        surface.blit(self.texture, (0, offset_int))


def _build_ambient_effect(effect_data: Dict) -> Optional[AmbientEffect]:
    effect_type = effect_data.get("type", "neon")
    if effect_type == "neon":
        rect = pygame.Rect(*effect_data.get("rect", [200, 68, 84, 24]))
        palette = [tuple(color) for color in effect_data.get("palette", [(220, 80, 120), (240, 200, 140), (160, 120, 240)])]
        speed = float(effect_data.get("speed", 0.35))
        label = effect_data.get("label", "OPEN")
        return NeonAmbient(rect, label, palette, speed)
    if effect_type == "rain":
        speed = float(effect_data.get("speed", 90.0))
        density = float(effect_data.get("density", 0.65))
        return RainAmbient(speed, density)
    return None


class Room:
    def __init__(self, data: Dict, hero: Hero) -> None:
        self.id = data["id"]
        self.name = data.get("name", self.id)
        background_name = data.get("background", self.id)
        priority_name = data.get("priority_mask", self.id)
        walkable_name = data.get("walkable_mask", self.id)
        self.background = assets.create_placeholder_background(background_name).convert()
        self.priority_mask = assets.create_priority_mask(priority_name).convert()
        self.priority_overlay = assets.create_priority_overlay(self.background, self.priority_mask)
        self.walkable_mask = assets.create_walkable_mask(walkable_name).convert()
        self.pathfinder = PathFinder(self.walkable_mask)
        self.hero = hero
        start = data.get("start_position", [WORLD_WIDTH // 2, WORLD_HEIGHT - 24])
        self.start_position = (start[0], start[1])

        self.ambient_effects: List[AmbientEffect] = []
        self.overlay_effects: List[AmbientEffect] = []
        for effect_data in data.get("ambient_effects", []):
            effect = _build_ambient_effect(effect_data)
            if not effect:
                continue
            if effect.layer == "overlay":
                self.overlay_effects.append(effect)
            else:
                self.ambient_effects.append(effect)

        self.hotspots: List[Hotspot] = []
        for hotspot_data in data.get("hotspots", []):
            actions = {}
            for verb, action in hotspot_data.get("actions", {}).items():
                if isinstance(action, str):
                    actions[verb.upper()] = HotspotAction(text=action)
                else:
                    messages = action.get("messages")
                    if isinstance(messages, list):
                        message_list = [str(m) for m in messages]
                    else:
                        message_list = []
                    actions[verb.upper()] = HotspotAction(
                        text=action.get("text", ""),
                        requires_item=action.get("requires_item"),
                        success_text=action.get("success_text"),
                        failure_text=action.get("failure_text"),
                        gives_item=action.get("gives_item"),
                        consumes_item=action.get("consumes_item", False),
                        change_room=action.get("change_room"),
                        set_state=action.get("set_state", {}),
                        messages=message_list,
                        once=action.get("once", False),
                        arrival_position=tuple(action.get("arrival_position", [])) if action.get("arrival_position") else None,
                    )
            rect = pygame.Rect(*hotspot_data["rect"])
            approach = [pygame.Vector2(point) for point in hotspot_data.get("approach_points", [])]
            self.hotspots.append(Hotspot(name=hotspot_data["name"], rect=rect, actions=actions, approach_points=approach))

        self.zombies: List[Zombie] = []
        for zombie_data in data.get("zombies", []):
            zombie = Zombie(tuple(zombie_data.get("position", (100, 100))))
            self.zombies.append(zombie)

    def find_hotspot(self, position: Tuple[int, int]) -> Optional[Hotspot]:
        for hotspot in self.hotspots:
            if hotspot.rect.collidepoint(position):
                return hotspot
        return None

    def update(self, dt: float) -> None:
        for zombie in self.zombies:
            zombie.update(dt, tuple(self.hero.position), self.pathfinder)
        for effect in self.ambient_effects:
            effect.update(dt)
        for effect in self.overlay_effects:
            effect.update(dt)

    def draw(self, surface: pygame.Surface) -> pygame.Rect:
        surface.blit(self.background, (0, 0))
        for effect in self.ambient_effects:
            effect.draw(surface)
        entities: List[Tuple[float, pygame.Surface, pygame.Rect, bool]] = []
        hero_image, hero_rect = self.hero.get_render()
        entities.append((hero_rect.bottom, hero_image, hero_rect, True))
        for zombie in self.zombies:
            image, rect = zombie.get_render()
            entities.append((rect.bottom, image, rect, False))
        entities.sort(key=lambda entry: entry[0])
        hero_rect_drawn = hero_rect
        for _, image, rect, is_hero in entities:
            surface.blit(image, rect)
            if self._is_rect_behind(rect):
                overlay = self._priority_slice(rect)
                surface.blit(overlay, rect)
            if is_hero:
                hero_rect_drawn = rect
        for effect in self.overlay_effects:
            effect.draw(surface)
        return hero_rect_drawn

    def _is_rect_behind(self, rect: pygame.Rect) -> bool:
        sample_points = [
            rect.midbottom,
            (rect.left + 2, rect.bottom - 1),
            (rect.right - 2, rect.bottom - 1),
        ]
        for x, y in sample_points:
            px = int(max(0, min(WORLD_WIDTH - 1, x)))
            py = int(max(0, min(WORLD_HEIGHT - 1, y)))
            if self.priority_mask.get_at((px, py))[0] > 127:
                return True
        return False

    def _priority_slice(self, rect: pygame.Rect) -> pygame.Surface:
        world_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        clipped = rect.clip(world_rect)
        if clipped.width == 0 or clipped.height == 0:
            return pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.blit(self.priority_overlay, (clipped.x - rect.x, clipped.y - rect.y), clipped)
        return overlay

    def is_point_walkable(self, point: pygame.Vector2) -> bool:
        x = int(max(0, min(WORLD_WIDTH - 1, point.x)))
        y = int(max(0, min(WORLD_HEIGHT - 1, point.y)))
        return self.walkable_mask.get_at((x, y))[0] > 127
