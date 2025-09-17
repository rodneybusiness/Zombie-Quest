"""Room and hotspot management for Zombie Quest."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

import assets
from pathfinding import AStarPathfinder

Vector2 = Tuple[float, float]


@dataclass
class Hotspot:
    hotspot_id: str
    name: str
    rect: pygame.Rect
    verbs: Dict[str, object]
    walk_to: Optional[Vector2]

    def get_action(self, verb: str) -> Optional[object]:
        return self.verbs.get(verb.lower())


class Room:
    def __init__(self, room_id: str, data: Dict[str, object]) -> None:
        self.room_id = room_id
        self.name: str = data.get("name", room_id.title())
        self.background = assets.get_background(data["background"])
        self.priority_mask = assets.get_priority_mask(data["priority_mask"])
        self.walk_mask_surface = assets.get_walk_mask(data["walk_mask"])
        self.walkbehind_overlay = assets.build_walkbehind_overlay(self.background, self.priority_mask)
        self.pathfinder = AStarPathfinder(self.walk_mask_surface, cell_size=data.get("cell_size", 8))
        self.start_position: Vector2 = tuple(data.get("start_position", (160, 150)))  # type: ignore[assignment]
        self.hotspots: List[Hotspot] = []
        self.zombie_data: List[Dict[str, object]] = data.get("zombies", [])
        self.entry_points: Dict[str, Vector2] = {
            key: tuple(value) for key, value in data.get("entry_points", {}).items()
        }
        self._walk_bounds = self._compute_walk_bounds()
        for hotspot_data in data.get("hotspots", []):
            rect = pygame.Rect(hotspot_data["rect"])
            walk_to = tuple(hotspot_data.get("walk_to", rect.center))  # type: ignore[arg-type]
            self.hotspots.append(
                Hotspot(
                    hotspot_data.get("id", hotspot_data["name"]),
                    hotspot_data.get("name", "Unknown"),
                    rect,
                    {key.lower(): value for key, value in hotspot_data.get("verbs", {}).items()},
                    walk_to,
                )
            )

    def _compute_walk_bounds(self) -> Tuple[float, float]:
        mask = pygame.mask.from_surface(self.walk_mask_surface)
        width, height = self.walk_mask_surface.get_size()
        min_y = height
        max_y = 0
        for y in range(height):
            for x in range(width):
                if mask.get_at((x, y)):
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        if min_y >= max_y:
            min_y, max_y = 100, 199
        return float(min_y), float(max_y)

    @property
    def walk_bounds(self) -> Tuple[float, float]:
        return self._walk_bounds

    def find_hotspot(self, position: Vector2) -> Optional[Hotspot]:
        point = (int(position[0]), int(position[1]))
        for hotspot in self.hotspots:
            if hotspot.rect.collidepoint(point):
                return hotspot
        return None

    def get_entry_point(self, entry_id: Optional[str]) -> Vector2:
        if entry_id and entry_id in self.entry_points:
            return self.entry_points[entry_id]
        return self.start_position
