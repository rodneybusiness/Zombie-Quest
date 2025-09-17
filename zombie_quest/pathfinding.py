from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

import pygame

GridPos = Tuple[int, int]
WorldPos = Tuple[float, float]


class GridPathfinder:
    def __init__(self, walkable_mask: pygame.Surface, cell_size: int = 4) -> None:
        self.cell_size = cell_size
        width, height = walkable_mask.get_size()
        self.grid_width = max(1, width // cell_size)
        self.grid_height = max(1, height // cell_size)
        self.walkable: List[List[bool]] = [
            [False for _ in range(self.grid_width)] for _ in range(self.grid_height)
        ]
        for gy in range(self.grid_height):
            for gx in range(self.grid_width):
                px = min(width - 1, gx * cell_size + cell_size // 2)
                py = min(height - 1, gy * cell_size + cell_size // 2)
                color = walkable_mask.get_at((px, py))
                self.walkable[gy][gx] = color[0] > 0 or color[1] > 0 or color[2] > 0

    def world_to_grid(self, position: WorldPos) -> GridPos:
        return int(position[0] // self.cell_size), int(position[1] // self.cell_size)

    def grid_to_world(self, position: GridPos) -> WorldPos:
        gx, gy = position
        x = gx * self.cell_size + self.cell_size / 2
        y = gy * self.cell_size + self.cell_size / 2
        return x, y

    def is_within(self, grid_pos: GridPos) -> bool:
        gx, gy = grid_pos
        return 0 <= gx < self.grid_width and 0 <= gy < self.grid_height

    def is_walkable_cell(self, grid_pos: GridPos) -> bool:
        gx, gy = grid_pos
        return self.is_within(grid_pos) and self.walkable[gy][gx]

    def _neighbors(self, grid_pos: GridPos) -> List[GridPos]:
        gx, gy = grid_pos
        neighbors: List[GridPos] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = (gx + dx, gy + dy)
                if not self.is_walkable_cell(neighbor):
                    continue
                if abs(dx) + abs(dy) == 2:
                    # Prevent diagonal corner cutting
                    if not (self.is_walkable_cell((gx + dx, gy)) and self.is_walkable_cell((gx, gy + dy))):
                        continue
                neighbors.append(neighbor)
        return neighbors

    def _heuristic(self, a: GridPos, b: GridPos) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _reconstruct_path(
        self, came_from: Dict[GridPos, GridPos], current: GridPos
    ) -> List[GridPos]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def find_nearest_walkable(self, target: GridPos, max_radius: int = 5) -> Optional[GridPos]:
        if self.is_walkable_cell(target):
            return target
        queue: List[GridPos] = [target]
        visited = {target}
        while queue:
            current = queue.pop(0)
            if self.is_walkable_cell(current):
                return current
            cx, cy = current
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (cx + dx, cy + dy)
                    if neighbor in visited:
                        continue
                    if abs(neighbor[0] - target[0]) > max_radius or abs(neighbor[1] - target[1]) > max_radius:
                        continue
                    visited.add(neighbor)
                    queue.append(neighbor)
        return None

    def find_path(self, start: WorldPos, goal: WorldPos) -> List[WorldPos]:
        start_grid = self.world_to_grid(start)
        goal_grid = self.world_to_grid(goal)

        if not self.is_walkable_cell(start_grid):
            nearest_start = self.find_nearest_walkable(start_grid, max_radius=8)
            if nearest_start is None:
                return []
            start_grid = nearest_start

        if not self.is_walkable_cell(goal_grid):
            nearest_goal = self.find_nearest_walkable(goal_grid, max_radius=12)
            if nearest_goal is None:
                return []
            goal_grid = nearest_goal

        open_heap: List[Tuple[float, GridPos]] = []
        heapq.heappush(open_heap, (0, start_grid))

        came_from: Dict[GridPos, GridPos] = {}
        g_score: Dict[GridPos, float] = {start_grid: 0.0}
        f_score: Dict[GridPos, float] = {start_grid: self._heuristic(start_grid, goal_grid)}
        open_set = {start_grid}

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current == goal_grid:
                path = self._reconstruct_path(came_from, current)
                return [self.grid_to_world(node) for node in path]

            open_set.discard(current)

            for neighbor in self._neighbors(current):
                tentative_g = g_score[current] + self._heuristic(current, neighbor)
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score_neighbor = tentative_g + self._heuristic(neighbor, goal_grid)
                    f_score[neighbor] = f_score_neighbor
                    if neighbor not in open_set:
                        heapq.heappush(open_heap, (f_score_neighbor, neighbor))
                        open_set.add(neighbor)
        return []
