"""Pathfinding utilities using a grid derived from walkable masks."""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import pygame

Vector2 = Tuple[float, float]
GridPos = Tuple[int, int]


@dataclass(order=True)
class PrioritizedItem:
    priority: float
    node: GridPos


class AStarPathfinder:
    """A star search over a coarse grid derived from a room walk mask."""

    def __init__(self, walk_surface: pygame.Surface, cell_size: int = 8) -> None:
        self.walk_surface = walk_surface
        self.cell_size = cell_size
        self.surface_width, self.surface_height = walk_surface.get_size()
        self.grid_width = self.surface_width // cell_size
        self.grid_height = self.surface_height // cell_size
        self.walk_mask = pygame.mask.from_surface(walk_surface)

    def to_grid(self, position: Vector2) -> GridPos:
        x, y = position
        grid_x = max(0, min(self.grid_width - 1, int(x // self.cell_size)))
        grid_y = max(0, min(self.grid_height - 1, int(y // self.cell_size)))
        return grid_x, grid_y

    def to_world(self, node: GridPos) -> Vector2:
        x = node[0] * self.cell_size + self.cell_size / 2
        y = node[1] * self.cell_size + self.cell_size / 2
        return x, y

    def _is_walkable_node(self, node: GridPos) -> bool:
        px = min(self.surface_width - 1, max(0, int(node[0] * self.cell_size + self.cell_size / 2)))
        py = min(self.surface_height - 1, max(0, int(node[1] * self.cell_size + self.cell_size / 2)))
        return bool(self.walk_mask.get_at((px, py)))

    def find_closest_walkable(self, node: GridPos, search_radius: int = 4) -> Optional[GridPos]:
        if self._is_walkable_node(node):
            return node
        for radius in range(1, search_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    candidate = (node[0] + dx, node[1] + dy)
                    if not self._in_bounds(candidate):
                        continue
                    if self._is_walkable_node(candidate):
                        return candidate
        return None

    def _in_bounds(self, node: GridPos) -> bool:
        return 0 <= node[0] < self.grid_width and 0 <= node[1] < self.grid_height

    def _neighbors(self, node: GridPos) -> Iterable[GridPos]:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = (node[0] + dx, node[1] + dy)
                if not self._in_bounds(neighbor):
                    continue
                if self._is_walkable_node(neighbor):
                    yield neighbor

    @staticmethod
    def _heuristic(a: GridPos, b: GridPos) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start: Vector2, goal: Vector2) -> List[Vector2]:
        start_node = self.find_closest_walkable(self.to_grid(start))
        goal_node = self.find_closest_walkable(self.to_grid(goal))
        if start_node is None or goal_node is None:
            return []

        frontier: List[PrioritizedItem] = []
        heapq.heappush(frontier, PrioritizedItem(0, start_node))
        came_from: Dict[GridPos, Optional[GridPos]] = {start_node: None}
        cost_so_far: Dict[GridPos, float] = {start_node: 0.0}

        while frontier:
            current = heapq.heappop(frontier).node

            if current == goal_node:
                break

            for neighbor in self._neighbors(current):
                new_cost = cost_so_far[current] + self._cost(current, neighbor)
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self._heuristic(neighbor, goal_node)
                    heapq.heappush(frontier, PrioritizedItem(priority, neighbor))
                    came_from[neighbor] = current

        if goal_node not in came_from:
            return []

        path_nodes: List[GridPos] = []
        current = goal_node
        while current != start_node:
            path_nodes.append(current)
            current = came_from[current]
        path_nodes.reverse()

        return [self.to_world(node) for node in path_nodes]

    @staticmethod
    def _cost(a: GridPos, b: GridPos) -> float:
        if a[0] != b[0] and a[1] != b[1]:
            return 1.414
        return 1.0
