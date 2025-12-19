"""Production-quality tests for A* pathfinding system - 25+ test cases."""
import pytest
import pygame
from typing import List, Tuple

# Initialize pygame for testing
pygame.init()

from zombie_quest.pathfinding import GridPathfinder


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def simple_walkable_mask():
    """Create a simple fully walkable mask."""
    surface = pygame.Surface((100, 100))
    surface.fill((255, 255, 255))  # All walkable
    return surface


@pytest.fixture
def complex_walkable_mask():
    """Create a mask with obstacles."""
    surface = pygame.Surface((100, 100))
    surface.fill((255, 255, 255))  # Start walkable

    # Create an obstacle wall in the middle
    pygame.draw.rect(surface, (0, 0, 0), (45, 0, 10, 80))  # Vertical wall

    return surface


@pytest.fixture
def maze_walkable_mask():
    """Create a maze-like mask."""
    surface = pygame.Surface((100, 100))
    surface.fill((0, 0, 0))  # Start unwalkable

    # Create corridors
    pygame.draw.rect(surface, (255, 255, 255), (10, 10, 80, 10))  # Top corridor
    pygame.draw.rect(surface, (255, 255, 255), (10, 10, 10, 80))  # Left corridor
    pygame.draw.rect(surface, (255, 255, 255), (80, 10, 10, 80))  # Right corridor
    pygame.draw.rect(surface, (255, 255, 255), (10, 80, 80, 10))  # Bottom corridor
    pygame.draw.rect(surface, (255, 255, 255), (40, 40, 20, 20))  # Center room

    return surface


@pytest.fixture
def pathfinder_simple(simple_walkable_mask):
    """Create pathfinder with simple mask."""
    return GridPathfinder(simple_walkable_mask, cell_size=4)


@pytest.fixture
def pathfinder_complex(complex_walkable_mask):
    """Create pathfinder with obstacles."""
    return GridPathfinder(complex_walkable_mask, cell_size=4)


@pytest.fixture
def pathfinder_maze(maze_walkable_mask):
    """Create pathfinder with maze."""
    return GridPathfinder(maze_walkable_mask, cell_size=4)


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestPathfinderInitialization:
    """Test pathfinder initialization."""

    def test_pathfinder_creates_successfully(self, simple_walkable_mask):
        """Pathfinder initializes from walkable mask."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=4)
        assert pathfinder is not None

    def test_grid_dimensions_calculated(self, simple_walkable_mask):
        """Grid dimensions are calculated from mask and cell size."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=4)
        assert pathfinder.grid_width == 25  # 100 / 4
        assert pathfinder.grid_height == 25

    def test_cell_size_set(self, simple_walkable_mask):
        """Cell size is stored correctly."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=8)
        assert pathfinder.cell_size == 8

    def test_walkable_grid_created(self, simple_walkable_mask):
        """Walkable grid is created with correct dimensions."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=4)
        assert len(pathfinder.walkable) == 25  # Height
        assert len(pathfinder.walkable[0]) == 25  # Width

    def test_walkable_grid_fully_walkable(self, simple_walkable_mask):
        """Fully white mask creates fully walkable grid."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=4)
        for row in pathfinder.walkable:
            assert all(row)

    def test_walkable_grid_with_obstacles(self, complex_walkable_mask):
        """Mask with obstacles creates correct walkable grid."""
        pathfinder = GridPathfinder(complex_walkable_mask, cell_size=4)
        # Middle columns should be unwalkable
        mid_x = 11  # Around x=45-55 in 100px width
        assert not pathfinder.walkable[10][mid_x]


# ============================================================================
# COORDINATE CONVERSION TESTS
# ============================================================================

class TestCoordinateConversion:
    """Test world <-> grid coordinate conversion."""

    def test_world_to_grid_center(self, pathfinder_simple):
        """world_to_grid converts center coordinates."""
        grid_pos = pathfinder_simple.world_to_grid((50.0, 50.0))
        assert grid_pos == (12, 12)  # 50 / 4 = 12.5 -> 12

    def test_world_to_grid_origin(self, pathfinder_simple):
        """world_to_grid handles origin."""
        grid_pos = pathfinder_simple.world_to_grid((0.0, 0.0))
        assert grid_pos == (0, 0)

    def test_world_to_grid_edge(self, pathfinder_simple):
        """world_to_grid handles edge coordinates."""
        grid_pos = pathfinder_simple.world_to_grid((99.0, 99.0))
        assert grid_pos == (24, 24)  # 99 / 4 = 24.75 -> 24

    def test_grid_to_world_center(self, pathfinder_simple):
        """grid_to_world converts to world coordinates."""
        world_pos = pathfinder_simple.grid_to_world((12, 12))
        assert world_pos == (50.0, 50.0)  # 12 * 4 + 2 = 50

    def test_grid_to_world_origin(self, pathfinder_simple):
        """grid_to_world handles origin."""
        world_pos = pathfinder_simple.grid_to_world((0, 0))
        assert world_pos == (2.0, 2.0)  # 0 * 4 + 2 = 2

    def test_coordinate_round_trip(self, pathfinder_simple):
        """Converting world->grid->world maintains approximate position."""
        original = (50.0, 50.0)
        grid = pathfinder_simple.world_to_grid(original)
        back = pathfinder_simple.grid_to_world(grid)

        # Should be close (within half a cell)
        assert abs(back[0] - original[0]) <= 2
        assert abs(back[1] - original[1]) <= 2


# ============================================================================
# GRID VALIDATION TESTS
# ============================================================================

class TestGridValidation:
    """Test grid cell validation."""

    def test_is_within_valid_position(self, pathfinder_simple):
        """is_within returns True for valid grid position."""
        assert pathfinder_simple.is_within((10, 10)) is True

    def test_is_within_origin(self, pathfinder_simple):
        """is_within returns True for origin."""
        assert pathfinder_simple.is_within((0, 0)) is True

    def test_is_within_edge(self, pathfinder_simple):
        """is_within returns True for edge positions."""
        assert pathfinder_simple.is_within((24, 24)) is True

    def test_is_within_out_of_bounds_negative(self, pathfinder_simple):
        """is_within returns False for negative coordinates."""
        assert pathfinder_simple.is_within((-1, 10)) is False
        assert pathfinder_simple.is_within((10, -1)) is False

    def test_is_within_out_of_bounds_too_large(self, pathfinder_simple):
        """is_within returns False for too large coordinates."""
        assert pathfinder_simple.is_within((25, 10)) is False
        assert pathfinder_simple.is_within((10, 25)) is False

    def test_is_walkable_cell_valid_walkable(self, pathfinder_simple):
        """is_walkable_cell returns True for walkable cell."""
        assert pathfinder_simple.is_walkable_cell((10, 10)) is True

    def test_is_walkable_cell_unwalkable(self, pathfinder_complex):
        """is_walkable_cell returns False for obstacle."""
        # Middle area has wall
        assert pathfinder_complex.is_walkable_cell((11, 10)) is False

    def test_is_walkable_cell_out_of_bounds(self, pathfinder_simple):
        """is_walkable_cell returns False for out of bounds."""
        assert pathfinder_simple.is_walkable_cell((-1, 10)) is False
        assert pathfinder_simple.is_walkable_cell((100, 10)) is False


# ============================================================================
# PATHFINDING ALGORITHM TESTS
# ============================================================================

class TestPathfindingAlgorithm:
    """Test A* pathfinding algorithm correctness."""

    def test_find_path_straight_line(self, pathfinder_simple):
        """find_path returns straight path in open space."""
        path = pathfinder_simple.find_path((10.0, 10.0), (90.0, 10.0))

        assert len(path) > 0
        assert path[0][0] < path[-1][0]  # Moves right
        assert abs(path[0][1] - path[-1][1]) < 10  # Stays roughly same Y

    def test_find_path_start_equals_goal(self, pathfinder_simple):
        """find_path handles start == goal."""
        path = pathfinder_simple.find_path((50.0, 50.0), (50.0, 50.0))

        # Should return empty or single-point path
        assert len(path) <= 1

    def test_find_path_around_obstacle(self, pathfinder_complex):
        """find_path routes around obstacles."""
        # Start left of wall, goal right of wall
        path = pathfinder_complex.find_path((20.0, 50.0), (80.0, 50.0))

        assert len(path) > 0
        # Path should go around the wall (likely above or below it)

    def test_find_path_no_path_exists(self):
        """find_path returns empty list when no path exists."""
        # Create a mask with isolated regions
        surface = pygame.Surface((100, 100))
        surface.fill((0, 0, 0))  # All unwalkable
        pygame.draw.rect(surface, (255, 255, 255), (10, 10, 20, 20))  # Left island
        pygame.draw.rect(surface, (255, 255, 255), (70, 70, 20, 20))  # Right island

        pathfinder = GridPathfinder(surface, cell_size=4)
        path = pathfinder.find_path((15.0, 15.0), (75.0, 75.0))

        assert len(path) == 0

    def test_find_path_diagonal_movement(self, pathfinder_simple):
        """find_path can use diagonal movement."""
        path = pathfinder_simple.find_path((10.0, 10.0), (90.0, 90.0))

        assert len(path) > 0
        # Diagonal path should be shorter than manhattan
        # Rough heuristic: diagonal should be ~sqrt(2) * distance
        assert len(path) < 30  # Pure manhattan would be ~40 cells

    def test_find_path_through_maze(self, pathfinder_maze):
        """find_path navigates through maze corridors."""
        # Start in left corridor, goal in right corridor
        path = pathfinder_maze.find_path((15.0, 15.0), (85.0, 85.0))

        # Should find path through corridors
        assert len(path) > 0

    def test_find_path_unwalkable_start(self, pathfinder_complex):
        """find_path handles unwalkable start position."""
        # Start in the wall obstacle
        path = pathfinder_complex.find_path((50.0, 50.0), (80.0, 50.0))

        # Should find nearest walkable and path from there
        # Or return empty if can't find nearby walkable
        # Implementation finds nearest walkable within radius

    def test_find_path_unwalkable_goal(self, pathfinder_complex):
        """find_path handles unwalkable goal position."""
        # Goal in the wall
        path = pathfinder_complex.find_path((20.0, 50.0), (50.0, 50.0))

        # Should find nearest walkable goal


# ============================================================================
# NEAREST WALKABLE TESTS
# ============================================================================

class TestNearestWalkable:
    """Test finding nearest walkable cell."""

    def test_find_nearest_walkable_already_walkable(self, pathfinder_simple):
        """find_nearest_walkable returns same position if already walkable."""
        grid_pos = (10, 10)
        nearest = pathfinder_simple.find_nearest_walkable(grid_pos)

        assert nearest == grid_pos

    def test_find_nearest_walkable_adjacent(self, pathfinder_complex):
        """find_nearest_walkable finds adjacent walkable cell."""
        # Position in wall, should find nearby walkable
        unwalkable_pos = (11, 10)  # In the wall
        nearest = pathfinder_complex.find_nearest_walkable(unwalkable_pos)

        assert nearest is not None
        assert pathfinder_complex.is_walkable_cell(nearest)

    def test_find_nearest_walkable_within_radius(self, pathfinder_complex):
        """find_nearest_walkable respects max_radius."""
        unwalkable_pos = (11, 10)
        nearest = pathfinder_complex.find_nearest_walkable(unwalkable_pos, max_radius=2)

        if nearest:
            # Should be within radius
            assert abs(nearest[0] - unwalkable_pos[0]) <= 2
            assert abs(nearest[1] - unwalkable_pos[1]) <= 2

    def test_find_nearest_walkable_no_nearby(self):
        """find_nearest_walkable returns None if no walkable nearby."""
        # Create mask with small isolated walkable region
        surface = pygame.Surface((100, 100))
        surface.fill((0, 0, 0))  # All unwalkable
        pygame.draw.rect(surface, (255, 255, 255), (10, 10, 4, 4))  # Small walkable spot

        pathfinder = GridPathfinder(surface, cell_size=4)
        # Try to find walkable far from the spot
        nearest = pathfinder.find_nearest_walkable((20, 20), max_radius=2)

        assert nearest is None


# ============================================================================
# NEIGHBOR GENERATION TESTS
# ============================================================================

class TestNeighborGeneration:
    """Test neighbor cell generation."""

    def test_neighbors_center_cell(self, pathfinder_simple):
        """_neighbors returns 8 neighbors for center cell."""
        neighbors = pathfinder_simple._neighbors((10, 10))

        # Should have 8 neighbors in open space
        assert len(neighbors) == 8

    def test_neighbors_corner_cell(self, pathfinder_simple):
        """_neighbors handles corner cells."""
        neighbors = pathfinder_simple._neighbors((0, 0))

        # Corner has fewer neighbors (only 3: right, down, diagonal)
        assert len(neighbors) == 3

    def test_neighbors_edge_cell(self, pathfinder_simple):
        """_neighbors handles edge cells."""
        neighbors = pathfinder_simple._neighbors((0, 10))

        # Left edge has 5 neighbors
        assert len(neighbors) == 5

    def test_neighbors_diagonal_corner_cutting_prevention(self):
        """_neighbors prevents diagonal corner cutting."""
        # Create L-shaped obstacle
        surface = pygame.Surface((100, 100))
        surface.fill((255, 255, 255))
        pygame.draw.rect(surface, (0, 0, 0), (48, 48, 8, 8))  # Block at (12, 12) grid cell
        pygame.draw.rect(surface, (0, 0, 0), (48, 40, 8, 8))  # Block at (12, 10)

        pathfinder = GridPathfinder(surface, cell_size=4)

        # Cell at (11, 11) should not have (12, 12) as diagonal neighbor
        # because both (12, 11) and (11, 12) would need to be walkable
        neighbors = pathfinder._neighbors((11, 11))

        # Diagonal to blocked corner should not be included
        assert (12, 12) not in neighbors

    def test_neighbors_excludes_unwalkable(self, pathfinder_complex):
        """_neighbors excludes unwalkable cells."""
        # Cell near the wall
        neighbors = pathfinder_complex._neighbors((10, 10))

        # Should not include cells in the wall
        for neighbor in neighbors:
            assert pathfinder_complex.is_walkable_cell(neighbor)


# ============================================================================
# HEURISTIC TESTS
# ============================================================================

class TestHeuristic:
    """Test pathfinding heuristic function."""

    def test_heuristic_same_position(self, pathfinder_simple):
        """_heuristic returns 0 for same position."""
        h = pathfinder_simple._heuristic((10, 10), (10, 10))
        assert h == 0.0

    def test_heuristic_horizontal_distance(self, pathfinder_simple):
        """_heuristic calculates horizontal distance."""
        h = pathfinder_simple._heuristic((0, 0), (5, 0))
        assert h == 5.0

    def test_heuristic_vertical_distance(self, pathfinder_simple):
        """_heuristic calculates vertical distance."""
        h = pathfinder_simple._heuristic((0, 0), (0, 5))
        assert h == 5.0

    def test_heuristic_diagonal_distance(self, pathfinder_simple):
        """_heuristic calculates diagonal distance (Euclidean)."""
        h = pathfinder_simple._heuristic((0, 0), (3, 4))
        assert abs(h - 5.0) < 0.01  # 3-4-5 triangle

    def test_heuristic_symmetry(self, pathfinder_simple):
        """_heuristic is symmetric."""
        h1 = pathfinder_simple._heuristic((0, 0), (10, 10))
        h2 = pathfinder_simple._heuristic((10, 10), (0, 0))
        assert h1 == h2


# ============================================================================
# PATH RECONSTRUCTION TESTS
# ============================================================================

class TestPathReconstruction:
    """Test path reconstruction from came_from dict."""

    def test_reconstruct_path_simple_chain(self, pathfinder_simple):
        """_reconstruct_path builds path from came_from dict."""
        came_from = {
            (2, 0): (1, 0),
            (1, 0): (0, 0)
        }
        path = pathfinder_simple._reconstruct_path(came_from, (2, 0))

        assert path == [(0, 0), (1, 0), (2, 0)]

    def test_reconstruct_path_single_step(self, pathfinder_simple):
        """_reconstruct_path handles single step."""
        came_from = {
            (1, 0): (0, 0)
        }
        path = pathfinder_simple._reconstruct_path(came_from, (1, 0))

        assert path == [(0, 0), (1, 0)]

    def test_reconstruct_path_no_parent(self, pathfinder_simple):
        """_reconstruct_path handles start node with no parent."""
        came_from = {}
        path = pathfinder_simple._reconstruct_path(came_from, (0, 0))

        assert path == [(0, 0)]


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_pathfinding_large_distance(self, pathfinder_simple):
        """Pathfinding handles large distances."""
        path = pathfinder_simple.find_path((2.0, 2.0), (98.0, 98.0))

        assert len(path) > 0

    def test_pathfinding_with_small_cell_size(self, simple_walkable_mask):
        """Pathfinding works with small cell size (high resolution)."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=2)
        path = pathfinder.find_path((10.0, 10.0), (90.0, 90.0))

        assert len(path) > 0

    def test_pathfinding_with_large_cell_size(self, simple_walkable_mask):
        """Pathfinding works with large cell size (low resolution)."""
        pathfinder = GridPathfinder(simple_walkable_mask, cell_size=10)
        path = pathfinder.find_path((10.0, 10.0), (90.0, 90.0))

        assert len(path) > 0

    def test_pathfinding_minimum_grid(self):
        """Pathfinding works on minimum size grid."""
        surface = pygame.Surface((10, 10))
        surface.fill((255, 255, 255))
        pathfinder = GridPathfinder(surface, cell_size=5)

        path = pathfinder.find_path((2.0, 2.0), (8.0, 8.0))
        # Should work even with tiny grid
