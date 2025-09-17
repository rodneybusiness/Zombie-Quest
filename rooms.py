"""Room and hotspot definitions for Zombie Quest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import pygame

import assets
from characters import Hero, Zombie
from pathfinding import PathFinder
from settings import WORLD_HEIGHT, WORLD_WIDTH


@dataclass
class HotspotAction:
    text: str
    requires_item: Optional[str] = None
    success_text: Optional[str] = None
    failure_text: Optional[str] = None
    gives_item: Optional[str] = None
    consumes_item: bool = False


@dataclass
class Hotspot:
    name: str
    rect: pygame.Rect
    actions: Dict[str, HotspotAction] = field(default_factory=dict)
    state: Dict[str, bool] = field(default_factory=dict)

    def action_for(self, verb: str) -> Optional[HotspotAction]:
        return self.actions.get(verb.upper())


class Room:
    def __init__(self, data: Dict, hero: Hero) -> None:
        self.id = data["id"]
        self.name = data.get("name", self.id)
        background_name = data.get("background", self.id)
        priority_name = data.get("priority_mask", self.id)
        walkable_name = data.get("walkable_mask", self.id)
        self.background = assets.create_placeholder_background(background_name).convert()
        self.priority_mask = assets.create_priority_mask(priority_name).convert()
        self.walkable_mask = assets.create_walkable_mask(walkable_name).convert()
        self.pathfinder = PathFinder(self.walkable_mask)
        self.hero = hero
        start = data.get("start_position", [WORLD_WIDTH // 2, WORLD_HEIGHT - 24])
        self.start_position = (start[0], start[1])

        self.hotspots: List[Hotspot] = []
        for hotspot_data in data.get("hotspots", []):
            actions = {}
            for verb, action in hotspot_data.get("actions", {}).items():
                if isinstance(action, str):
                    actions[verb.upper()] = HotspotAction(text=action)
                else:
                    actions[verb.upper()] = HotspotAction(
                        text=action.get("text", ""),
                        requires_item=action.get("requires_item"),
                        success_text=action.get("success_text"),
                        failure_text=action.get("failure_text"),
                        gives_item=action.get("gives_item"),
                        consumes_item=action.get("consumes_item", False),
                    )
            rect = pygame.Rect(*hotspot_data["rect"])
            self.hotspots.append(Hotspot(name=hotspot_data["name"], rect=rect, actions=actions))

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

    def draw(self, surface: pygame.Surface) -> pygame.Rect:
        surface.blit(self.background, (0, 0))
        entities: List[Tuple[float, Zombie, pygame.Surface, pygame.Rect, bool]] = []
        hero_image, hero_rect = self.hero.get_render()
        entities.append((hero_rect.bottom, self.hero, hero_image, hero_rect, True))
        for zombie in self.zombies:
            image, rect = zombie.get_render()
            entities.append((rect.bottom, zombie, image, rect, False))
        entities.sort(key=lambda entry: entry[0])
        hero_rect_drawn: Optional[pygame.Rect] = None
        for _, entity, image, rect, is_hero in entities:
            surface.blit(image, rect)
            if is_hero:
                hero_rect_drawn = rect
        if hero_rect_drawn and self._is_position_behind(hero_rect_drawn.midbottom):
            overlay = self._priority_slice(hero_rect_drawn)
            surface.blit(overlay, hero_rect_drawn)
        return hero_rect_drawn if hero_rect_drawn else hero_rect

    def _is_position_behind(self, position: Tuple[float, float]) -> bool:
        x = int(max(0, min(WORLD_WIDTH - 1, position[0])))
        y = int(max(0, min(WORLD_HEIGHT - 1, position[1] - 1)))
        return self.priority_mask.get_at((x, y))[0] > 127

    def _priority_slice(self, rect: pygame.Rect) -> pygame.Surface:
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        for y in range(rect.height):
            world_y = rect.top + y
            if not (0 <= world_y < WORLD_HEIGHT):
                continue
            for x in range(rect.width):
                world_x = rect.left + x
                if 0 <= world_x < WORLD_WIDTH and self.priority_mask.get_at((world_x, world_y))[0] > 127:
                    color = self.background.get_at((world_x, world_y))
                    overlay.set_at((x, y), (*color[:3], 255))
        return overlay
