"""Pytest configuration and shared fixtures for all tests.

This module provides:
- Mock infrastructure for pygame, audio, and display
- Reusable test fixtures for rooms, heroes, zombies
- Test data generators
- Headless testing utilities
"""
import pytest
import pygame
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Optional
import sys

# Initialize pygame once for all tests
pygame.init()

from zombie_quest.rooms import Room, Hotspot
from zombie_quest.characters import Hero, Zombie
from zombie_quest.ui import Item, Verb
from zombie_quest.config import GAMEPLAY


# ============================================================================
# MOCK INFRASTRUCTURE
# ============================================================================

class MockPygameDisplay:
    """Mock pygame display to prevent window creation in tests."""

    def __init__(self):
        self.surface = MagicMock(spec=pygame.Surface)
        self.caption = ""

    def set_mode(self, size, flags=0):
        """Mock set_mode."""
        self.surface = MagicMock(spec=pygame.Surface)
        self.surface.get_size.return_value = size
        return self.surface

    def set_caption(self, caption):
        """Mock set_caption."""
        self.caption = caption

    def flip(self):
        """Mock flip."""
        pass


class MockAudioManager:
    """Mock audio manager for testing without sound."""

    def __init__(self):
        self.sounds_played = []
        self.music_playing = False

    def play(self, sound_name, volume=1.0):
        """Record sound play."""
        self.sounds_played.append((sound_name, volume))

    def play_music(self, track_name, loop=True):
        """Record music play."""
        self.music_playing = True

    def stop_music(self):
        """Stop music."""
        self.music_playing = False

    def get_played_sounds(self):
        """Get list of played sounds."""
        return self.sounds_played

    def reset(self):
        """Reset tracking."""
        self.sounds_played = []
        self.music_playing = False


class MockRoom:
    """Mock room for testing without full room initialization."""

    def __init__(self, room_id="mock_room", size=(320, 200)):
        self.id = room_id
        self.name = room_id.replace("_", " ").title()
        self.size = size
        self.bounds = pygame.Rect(0, 0, size[0], size[1])
        self.hotspots = []
        self.zombies = []
        self.entry_message = f"You enter {self.name}."
        self.default_entry = (size[0] // 2, int(size[1] * 0.8))

        # Create minimal surfaces
        self.background = pygame.Surface(size)
        self.background.fill((50, 50, 50))
        self.walkable_mask = pygame.Surface(size)
        self.walkable_mask.fill((255, 255, 255))
        self.priority_mask = pygame.Surface(size)
        self.priority_mask.fill((0, 0, 0))

        from zombie_quest.pathfinding import GridPathfinder
        self.pathfinder = GridPathfinder(self.walkable_mask)

    def is_walkable(self, position):
        """All positions walkable in mock."""
        x, y = int(position[0]), int(position[1])
        if not self.bounds.collidepoint(x, y):
            return False
        return True

    def is_behind(self, position):
        """No priority regions in mock."""
        return False

    def find_hotspot(self, position):
        """Find hotspot at position."""
        for hotspot in self.hotspots:
            if hotspot.rect.collidepoint(position):
                return hotspot
        return None

    def draw(self, surface, hero):
        """Mock draw."""
        pass

    def update(self, dt, hero):
        """Mock update."""
        for zombie in self.zombies:
            zombie.update(dt, hero.foot_position, self.bounds)


class MockHero:
    """Mock hero for testing without full sprite loading."""

    def __init__(self, position=(100, 100)):
        self.position = pygame.Vector2(position)
        self.health = GAMEPLAY.HERO_MAX_HEALTH
        self.max_health = GAMEPLAY.HERO_MAX_HEALTH
        self.speed = GAMEPLAY.HERO_SPEED
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.path = []
        self.current_target = None
        self.using_keyboard = False
        self.keyboard_velocity = pygame.Vector2(0, 0)

    @property
    def foot_position(self):
        return (self.position.x, self.position.y)

    def has_arrived(self):
        return self.current_target is None and not self.path

    def take_damage(self, amount=1):
        if self.is_invincible:
            return False
        self.health = max(0, self.health - amount)
        self.is_invincible = True
        self.invincibility_timer = GAMEPLAY.HERO_INVINCIBILITY_TIME
        return self.health <= 0

    def heal(self, amount=1):
        self.health = min(self.max_health, self.health + amount)

    def is_dead(self):
        return self.health <= 0

    def update(self, dt, room_bounds=None, walkable_check=None):
        """Simplified update."""
        if self.is_invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False

    def set_destination(self, destination, pathfinder):
        """Set pathfinding destination."""
        self.current_target = pygame.Vector2(destination)
        self.path = []


# ============================================================================
# PYTEST FIXTURES - MOCKS
# ============================================================================

@pytest.fixture
def mock_display():
    """Mock pygame display."""
    mock = MockPygameDisplay()
    with patch('pygame.display.set_mode', mock.set_mode):
        with patch('pygame.display.set_caption', mock.set_caption):
            with patch('pygame.display.flip', mock.flip):
                yield mock


@pytest.fixture
def mock_audio():
    """Mock audio manager."""
    mock = MockAudioManager()
    with patch('zombie_quest.engine.get_audio_manager', return_value=mock):
        yield mock


@pytest.fixture
def headless_mode():
    """Enable headless mode for tests."""
    with patch('pygame.display.set_mode') as mock_display:
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_display.return_value = mock_surface
        yield


# ============================================================================
# PYTEST FIXTURES - GAME OBJECTS
# ============================================================================

@pytest.fixture
def mock_room():
    """Create a mock room."""
    return MockRoom()


@pytest.fixture
def mock_hero():
    """Create a mock hero."""
    return MockHero()


@pytest.fixture
def basic_hotspot():
    """Create a basic hotspot for testing."""
    return Hotspot(
        rect=pygame.Rect(50, 50, 40, 40),
        name="Test Hotspot",
        verbs={
            "look": "A test object.",
            "use": "You use it.",
            "talk": "It doesn't respond."
        }
    )


@pytest.fixture
def item_hotspot():
    """Create a hotspot that gives an item."""
    return Hotspot(
        rect=pygame.Rect(100, 100, 30, 30),
        name="Item Pedestal",
        verbs={
            "look": "A pedestal with an item.",
            "use": "You take the item."
        },
        give_item="Test Item",
        give_item_triggers=("use",)
    )


@pytest.fixture
def locked_hotspot():
    """Create a hotspot requiring an item."""
    return Hotspot(
        rect=pygame.Rect(150, 150, 40, 50),
        name="Locked Door",
        verbs={
            "look": "A locked door.",
            "use_missing": "You need a key.",
            "use_success": "The door unlocks!"
        },
        required_item="Key"
    )


@pytest.fixture
def transition_hotspot():
    """Create a hotspot that transitions rooms."""
    return Hotspot(
        rect=pygame.Rect(280, 80, 30, 50),
        name="Exit Door",
        verbs={
            "look": "An exit door.",
            "use": "You go through."
        },
        target_room="next_room",
        target_position=(50, 100),
        transition_verb="use"
    )


@pytest.fixture
def test_hero():
    """Create a real hero for testing."""
    return Hero((100, 100))


@pytest.fixture
def test_zombie():
    """Create a zombie for testing."""
    return Zombie((200, 200), zombie_type="scene")


@pytest.fixture
def test_item():
    """Create a test item."""
    return Item(
        name="Test Item",
        description="A test item for testing",
        icon_color=(200, 200, 200)
    )


# ============================================================================
# PYTEST FIXTURES - TEST DATA
# ============================================================================

@pytest.fixture
def minimal_room_data():
    """Minimal room data dictionary."""
    return {
        "id": "test_room",
        "name": "Test Room",
        "size": [320, 200],
        "background": {"label": "Test", "base_color": [50, 50, 50]},
        "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
        "hotspots": [],
        "zombies": []
    }


@pytest.fixture
def full_room_data():
    """Complete room data with all features."""
    return {
        "id": "full_room",
        "name": "Full Featured Room",
        "size": [320, 200],
        "entry_message": "You enter a fully featured room.",
        "default_entry": [160, 100],
        "background": {
            "label": "Full Room",
            "base_color": [60, 60, 60],
            "gradient": [[30, 10, 60], [70, 40, 140]],
            "accent_lines": [{"y": 100, "height": 5, "color": [255, 0, 0]}]
        },
        "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
        "priority_regions": [{"shape": "rect", "rect": [0, 80, 320, 40]}],
        "hotspots": [
            {
                "name": "Door",
                "rect": [280, 80, 30, 50],
                "verbs": {"look": "A door.", "use": "You open it."},
                "target_room": "other_room",
                "transition_verb": "use"
            }
        ],
        "zombies": [{"position": [200, 150], "type": "scene"}]
    }


@pytest.fixture
def game_data_two_rooms():
    """Game data with two connected rooms."""
    return {
        "hero": {"start_room": "room_a", "position": [50, 100]},
        "items": [
            {"name": "Key", "description": "A key", "icon_color": [255, 215, 0]}
        ],
        "starting_inventory": [],
        "rooms": [
            {
                "id": "room_a",
                "name": "Room A",
                "size": [320, 200],
                "background": {"label": "A", "base_color": [50, 50, 50]},
                "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
                "hotspots": [
                    {
                        "name": "Door to B",
                        "rect": [280, 80, 30, 50],
                        "verbs": {"use": "You go to room B."},
                        "target_room": "room_b",
                        "transition_verb": "use"
                    }
                ],
                "zombies": []
            },
            {
                "id": "room_b",
                "name": "Room B",
                "size": [320, 200],
                "background": {"label": "B", "base_color": [60, 60, 60]},
                "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
                "hotspots": [],
                "zombies": []
            }
        ]
    }


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "headless: mark test as headless-compatible"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Add markers based on test file
    for item in items:
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


# ============================================================================
# TEST UTILITIES
# ============================================================================

def create_test_surface(width=320, height=200, color=(50, 50, 50)):
    """Create a test surface."""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface


def create_walkable_surface(width=320, height=200, obstacles=None):
    """Create a walkable mask with optional obstacles."""
    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))  # All walkable

    if obstacles:
        for obstacle in obstacles:
            pygame.draw.rect(surface, (0, 0, 0), obstacle)

    return surface


def simulate_game_frames(engine, num_frames=10, dt=1/60):
    """Simulate multiple game frames."""
    for _ in range(num_frames):
        engine.update(dt)


def assert_hero_moved(initial_pos, current_pos, min_distance=1.0):
    """Assert hero moved at least min_distance."""
    distance = initial_pos.distance_to(current_pos)
    assert distance >= min_distance, f"Hero only moved {distance:.2f} pixels"


def assert_hero_near(hero_pos, target_pos, max_distance=10.0):
    """Assert hero is near target position."""
    distance = hero_pos.distance_to(pygame.Vector2(target_pos))
    assert distance <= max_distance, f"Hero is {distance:.2f} pixels away from target"


# Make utilities available to tests
pytest.create_test_surface = create_test_surface
pytest.create_walkable_surface = create_walkable_surface
pytest.simulate_game_frames = simulate_game_frames
pytest.assert_hero_moved = assert_hero_moved
pytest.assert_hero_near = assert_hero_near
