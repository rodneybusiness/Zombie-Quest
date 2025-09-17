from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

from .characters import Hero, Zombie
from .pathfinding import GridPathfinder
from .resources import (
    create_placeholder_background,
    create_priority_mask,
    create_walkable_mask,
    extract_priority_overlay,
)

RoomSize = Tuple[int, int]
VerbMessages = Dict[str, str]


@dataclass
class Hotspot:
    rect: pygame.Rect
    name: str
    verbs: VerbMessages
    walk_position: Optional[Tuple[int, int]] = None
    required_item: Optional[str] = None
    give_item: Optional[str] = None
    remove_item: Optional[str] = None
    talk_target: Optional[str] = None

    def message_for(self, verb: str, outcome: str = "default") -> str:
        if outcome != "default":
            key = f"{verb}_{outcome}"
            if key in self.verbs:
                return self.verbs[key]
        return self.verbs.get(verb, "Nothing happens.")


class Room:
    def __init__(self, data: Dict) -> None:
        self.id = data["id"]
        self.name = data.get("name", self.id.title())
        self.size: RoomSize = tuple(data.get("size", (320, 200)))  # type: ignore[assignment]
        self.background = create_placeholder_background(data.get("background_label", self.name), self.size)
        self.priority_mask = create_priority_mask(self.size, data.get("priority_regions", []))
        self.walkable_mask = create_walkable_mask(self.size, data.get("walkable_zones", []))
        self.priority_overlay = extract_priority_overlay(self.background, self.priority_mask)
        self.pathfinder = GridPathfinder(self.walkable_mask)
        self.bounds = pygame.Rect((0, 0), self.size)
        self.hotspots: List[Hotspot] = [self._create_hotspot(h) for h in data.get("hotspots", [])]
        self.zombies: List[Zombie] = [Zombie(tuple(z.get("position", (160, 120)))) for z in data.get("zombies", [])]

    def _create_hotspot(self, data: Dict) -> Hotspot:
        rect = pygame.Rect(data.get("rect", [0, 0, 10, 10]))
        verbs: VerbMessages = data.get("verbs", {})
        walk_position = tuple(data.get("walk_position")) if data.get("walk_position") else None
        return Hotspot(
            rect=rect,
            name=data.get("name", "Hotspot"),
            verbs=verbs,
            walk_position=walk_position,
            required_item=data.get("required_item"),
            give_item=data.get("give_item"),
            remove_item=data.get("remove_item"),
            talk_target=data.get("talk_target"),
        )

    def update(self, dt: float, hero: Hero) -> None:
        hero_position = hero.foot_position
        for zombie in self.zombies:
            zombie.update(dt, hero_position, self.bounds)

    def draw(self, surface: pygame.Surface, hero: Hero) -> None:
        surface.blit(self.background, (0, 0))
        characters: List = self.zombies + [hero]
        characters.sort(key=lambda c: c.position.y)
        hero_rect: Optional[pygame.Rect] = None
        hero_behind = False
        for character in characters:
            rect = character.draw(surface, self.size[1])
            if character is hero:
                hero_rect = rect
                hero_behind = self.is_behind(character.foot_position)
        if hero_behind and hero_rect:
            overlay_rect = hero_rect.clip(self.priority_overlay.get_rect())
            if overlay_rect.width > 0 and overlay_rect.height > 0:
                surface.blit(self.priority_overlay, overlay_rect.topleft, overlay_rect)

    def is_walkable(self, position: Tuple[float, float]) -> bool:
        x, y = int(position[0]), int(position[1])
        if not self.bounds.collidepoint(x, y):
            return False
        color = self.walkable_mask.get_at((x, y))
        return color[0] > 0 or color[1] > 0 or color[2] > 0

    def is_behind(self, position: Tuple[float, float]) -> bool:
        x, y = int(position[0]), int(position[1])
        if not self.bounds.collidepoint(x, y):
            return False
        color = self.priority_mask.get_at((x, y))
        return color[0] > 200 and color[1] > 200 and color[2] > 200

    def find_hotspot(self, position: Tuple[int, int]) -> Optional[Hotspot]:
        for hotspot in self.hotspots:
            if hotspot.rect.collidepoint(position):
                return hotspot
        return None
