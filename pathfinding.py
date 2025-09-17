"""Grid-based A* pathfinding used to navigate walkable masks."""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Tuple

import pygame

from settings import PATH_GRID_SIZE

GridPos = Tuple[int, int]
Point = Tuple[float, float]


class PathFinder:
    """Perform A* pathfinding across a walkable mask."""

    def __init__(self, walkable_mask: pygame.Surface, cell_size: int = PATH_GRID_SIZE) -> None:
        self.mask = walkable_mask
        self.cell_size = cell_size
        self.width = walkable_mask.get_width() // cell_size
        self.height = walkable_mask.get_height() // cell_size

    def point_to_cell(self, point: Point) -> GridPos:
        return int(point[0] // self.cell_size), int(point[1] // self.cell_size)

    def cell_to_point(self, cell: GridPos) -> Point:
        return (cell[0] * self.cell_size + self.cell_size / 2.0, cell[1] * self.cell_size + self.cell_size / 2.0)

    def _is_walkable_cell(self, cell: GridPos) -> bool:
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        pixel_x = int(x * self.cell_size + self.cell_size / 2)
        pixel_y = int(y * self.cell_size + self.cell_size / 2)
        color = self.mask.get_at((pixel_x, pixel_y))
        return color[0] > 127

    def _neighbors(self, cell: GridPos) -> List[Tuple[GridPos, float]]:
        x, y = cell
        neighbors: List[Tuple[GridPos, float]] = []
        cardinal = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for nx, ny in cardinal:
            neighbor = (nx, ny)
            if self._is_walkable_cell(neighbor):
                neighbors.append((neighbor, 1.0))

        diagonals = [
            (x + 1, y + 1, (x + 1, y), (x, y + 1)),
            (x - 1, y + 1, (x - 1, y), (x, y + 1)),
            (x + 1, y - 1, (x + 1, y), (x, y - 1)),
            (x - 1, y - 1, (x - 1, y), (x, y - 1)),
        ]
        for nx, ny, check_a, check_b in diagonals:
            neighbor = (nx, ny)
            if self._is_walkable_cell(neighbor) and self._is_walkable_cell(check_a) and self._is_walkable_cell(check_b):
                neighbors.append((neighbor, math.sqrt(2)))
        return neighbors

    @staticmethod
    def _heuristic(a: GridPos, b: GridPos) -> float:
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    def _nearest_walkable(self, start: GridPos) -> Optional[GridPos]:
        from collections import deque

        if self._is_walkable_cell(start):
            return start

        visited = set()
        queue = deque([start])
        while queue:
            cell = queue.popleft()
            if cell in visited:
                continue
            visited.add(cell)
            if self._is_walkable_cell(cell):
                return cell
            x, y = cell
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for neighbor in neighbors:
                if neighbor not in visited and 0 <= neighbor[0] < self.width and 0 <= neighbor[1] < self.height:
                    queue.append(neighbor)
        return None

    def find_path(self, start: Point, goal: Point) -> List[Point]:
        start_cell = self._nearest_walkable(self.point_to_cell(start))
        goal_cell = self._nearest_walkable(self.point_to_cell(goal))

        if start_cell is None or goal_cell is None:
            return []

        open_set: List[Tuple[float, GridPos]] = []
        heapq.heappush(open_set, (0.0, start_cell))
        came_from: Dict[GridPos, Optional[GridPos]] = {start_cell: None}
        g_score: Dict[GridPos, float] = {start_cell: 0.0}
        f_score: Dict[GridPos, float] = {start_cell: self._heuristic(start_cell, goal_cell)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal_cell:
                return self._reconstruct_path(came_from, current)

            for neighbor, cost in self._neighbors(current):
                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal_cell)
                    if neighbor not in [c for _, c in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def _reconstruct_path(self, came_from: Dict[GridPos, Optional[GridPos]], current: GridPos) -> List[Point]:
        path: List[Point] = [self.cell_to_point(current)]
        while came_from[current] is not None:
            current = came_from[current]
            path.append(self.cell_to_point(current))
        path.reverse()
        return self._smooth_path(path)

    def _smooth_path(self, points: List[Point]) -> List[Point]:
        if len(points) <= 2:
            return points
        smoothed = [points[0]]
        index = 0
        while index < len(points) - 1:
            next_index = len(points) - 1
            for candidate in range(len(points) - 1, index, -1):
                if self._line_walkable(points[index], points[candidate]):
                    next_index = candidate
                    break
            smoothed.append(points[next_index])
            index = next_index
        return smoothed

    def _line_walkable(self, start: Point, end: Point) -> bool:
        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0
        steps = int(max(abs(dx), abs(dy)) / max(1, self.cell_size // 2)) + 1
        for step in range(steps + 1):
            t = step / max(1, steps)
            x = x0 + dx * t
            y = y0 + dy * t
            if not self._is_walkable_point((x, y)):
                return False
        return True

    def _is_walkable_point(self, point: Point) -> bool:
        x = int(max(0, min(self.mask.get_width() - 1, point[0])))
        y = int(max(0, min(self.mask.get_height() - 1, point[1])))
        return self.mask.get_at((x, y))[0] > 127
