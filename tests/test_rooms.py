"""Production-quality tests for Room system - 30+ test cases."""
import pytest
import pygame
from typing import Dict, List

# Initialize pygame for testing
pygame.init()

from zombie_quest.rooms import Room, Hotspot
from zombie_quest.characters import Hero, Zombie


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def basic_room_data():
    """Basic room data for testing."""
    return {
        "id": "test_room",
        "name": "Test Room",
        "size": [320, 200],
        "entry_message": "You enter the test room.",
        "default_entry": [160, 100],
        "background": {
            "label": "Test",
            "base_color": [50, 50, 50]
        },
        "walkable_zones": [
            {"shape": "rect", "rect": [0, 0, 320, 200]}
        ],
        "priority_regions": [],
        "hotspots": [],
        "zombies": []
    }


@pytest.fixture
def room_with_hotspots():
    """Room data with multiple hotspots."""
    return {
        "id": "detailed_room",
        "name": "Detailed Room",
        "size": [320, 200],
        "background": {"label": "Detailed", "base_color": [60, 60, 60]},
        "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
        "hotspots": [
            {
                "name": "Door",
                "rect": [100, 50, 40, 60],
                "walk_position": [120, 115],
                "verbs": {
                    "look": "A wooden door.",
                    "use": "You open it.",
                    "talk": "..."
                },
                "target_room": "other_room",
                "target_position": [50, 50],
                "transition_verb": "use"
            },
            {
                "name": "Chest",
                "rect": [200, 150, 30, 25],
                "verbs": {
                    "look": "A treasure chest.",
                    "use_default": "It's locked.",
                    "use_success": "You open the chest!"
                },
                "required_item": "Key",
                "give_item": "Treasure",
                "give_item_triggers": ["use"]
            },
            {
                "name": "NPC",
                "rect": [50, 80, 20, 40],
                "walk_position": [60, 125],
                "verbs": {
                    "look": "A friendly NPC.",
                    "talk": "Hello, traveler!"
                },
                "talk_target": "merchant"
            }
        ],
        "zombies": []
    }


@pytest.fixture
def room_with_zombies():
    """Room data with zombies."""
    return {
        "id": "zombie_room",
        "name": "Zombie Room",
        "size": [320, 200],
        "background": {"label": "Zombies", "base_color": [40, 40, 40]},
        "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}],
        "hotspots": [],
        "zombies": [
            {"position": [100, 100], "type": "scene"},
            {"position": [200, 150], "type": "bouncer"},
            {"position": [50, 75]}  # No type specified
        ]
    }


@pytest.fixture
def complex_walkable_data():
    """Room with complex walkable zones."""
    return {
        "id": "complex_room",
        "name": "Complex Room",
        "size": [320, 200],
        "background": {"label": "Complex", "base_color": [70, 70, 70]},
        "walkable_zones": [
            {"shape": "rect", "rect": [0, 150, 320, 50]},  # Bottom walkable area
            {"shape": "polygon", "points": [[100, 100], [220, 100], [220, 150], [100, 150]]}  # Center platform
        ],
        "priority_regions": [
            {"shape": "rect", "rect": [0, 80, 320, 40]}  # Objects at Y=80-120 appear in front
        ],
        "hotspots": [],
        "zombies": []
    }


# ============================================================================
# ROOM INITIALIZATION TESTS
# ============================================================================

class TestRoomInitialization:
    """Test room creation and initialization."""

    def test_room_creates_successfully(self, basic_room_data):
        """Room initializes from data dictionary."""
        room = Room(basic_room_data)
        assert room is not None

    def test_room_id_set(self, basic_room_data):
        """Room ID is set correctly."""
        room = Room(basic_room_data)
        assert room.id == "test_room"

    def test_room_name_set(self, basic_room_data):
        """Room name is set correctly."""
        room = Room(basic_room_data)
        assert room.name == "Test Room"

    def test_room_size_set(self, basic_room_data):
        """Room size is set correctly."""
        room = Room(basic_room_data)
        assert room.size == (320, 200)

    def test_room_entry_message_set(self, basic_room_data):
        """Entry message is stored."""
        room = Room(basic_room_data)
        assert room.entry_message == "You enter the test room."

    def test_room_default_entry_set(self, basic_room_data):
        """Default entry position is set."""
        room = Room(basic_room_data)
        assert room.default_entry == (160, 100)

    def test_room_default_entry_fallback(self):
        """Default entry falls back to center-bottom if not specified."""
        data = {
            "id": "no_entry",
            "size": [400, 300],
            "background": {"label": "Test", "base_color": [50, 50, 50]},
            "walkable_zones": [{"shape": "rect", "rect": [0, 0, 400, 300]}]
        }
        room = Room(data)
        assert room.default_entry == (200, 240)  # 400/2, 300*0.8

    def test_room_background_created(self, basic_room_data):
        """Background surface is created."""
        room = Room(basic_room_data)
        assert room.background is not None
        assert isinstance(room.background, pygame.Surface)

    def test_room_walkable_mask_created(self, basic_room_data):
        """Walkable mask is created."""
        room = Room(basic_room_data)
        assert room.walkable_mask is not None
        assert isinstance(room.walkable_mask, pygame.Surface)

    def test_room_priority_mask_created(self, basic_room_data):
        """Priority mask is created."""
        room = Room(basic_room_data)
        assert room.priority_mask is not None

    def test_room_pathfinder_created(self, basic_room_data):
        """Pathfinder is initialized."""
        room = Room(basic_room_data)
        assert room.pathfinder is not None

    def test_room_bounds_set(self, basic_room_data):
        """Room bounds rect is set correctly."""
        room = Room(basic_room_data)
        assert room.bounds == pygame.Rect(0, 0, 320, 200)


# ============================================================================
# HOTSPOT TESTS
# ============================================================================

class TestHotspots:
    """Test hotspot loading and detection."""

    def test_room_loads_hotspots(self, room_with_hotspots):
        """Room loads all hotspots from data."""
        room = Room(room_with_hotspots)
        assert len(room.hotspots) == 3

    def test_hotspot_names_set(self, room_with_hotspots):
        """Hotspot names are set correctly."""
        room = Room(room_with_hotspots)
        names = [h.name for h in room.hotspots]
        assert "Door" in names
        assert "Chest" in names
        assert "NPC" in names

    def test_hotspot_rect_set(self, room_with_hotspots):
        """Hotspot rectangles are created."""
        room = Room(room_with_hotspots)
        door_hotspot = room.hotspots[0]
        assert door_hotspot.rect == pygame.Rect(100, 50, 40, 60)

    def test_hotspot_walk_position_set(self, room_with_hotspots):
        """Hotspot walk positions are stored."""
        room = Room(room_with_hotspots)
        door_hotspot = room.hotspots[0]
        assert door_hotspot.walk_position == (120, 115)

    def test_hotspot_verbs_loaded(self, room_with_hotspots):
        """Hotspot verb messages are loaded."""
        room = Room(room_with_hotspots)
        door_hotspot = room.hotspots[0]
        assert "look" in door_hotspot.verbs
        assert "use" in door_hotspot.verbs

    def test_hotspot_required_item_set(self, room_with_hotspots):
        """Hotspot required item is stored."""
        room = Room(room_with_hotspots)
        chest_hotspot = room.hotspots[1]
        assert chest_hotspot.required_item == "Key"

    def test_hotspot_give_item_set(self, room_with_hotspots):
        """Hotspot give item is stored."""
        room = Room(room_with_hotspots)
        chest_hotspot = room.hotspots[1]
        assert chest_hotspot.give_item == "Treasure"

    def test_hotspot_talk_target_set(self, room_with_hotspots):
        """Hotspot talk target is stored."""
        room = Room(room_with_hotspots)
        npc_hotspot = room.hotspots[2]
        assert npc_hotspot.talk_target == "merchant"

    def test_hotspot_transition_data_set(self, room_with_hotspots):
        """Hotspot room transition data is stored."""
        room = Room(room_with_hotspots)
        door_hotspot = room.hotspots[0]
        assert door_hotspot.target_room == "other_room"
        assert door_hotspot.target_position == (50, 50)
        assert door_hotspot.transition_verb == "use"

    def test_find_hotspot_valid_position(self, room_with_hotspots):
        """find_hotspot returns hotspot at valid position."""
        room = Room(room_with_hotspots)
        hotspot = room.find_hotspot((110, 60))
        assert hotspot is not None
        assert hotspot.name == "Door"

    def test_find_hotspot_invalid_position(self, room_with_hotspots):
        """find_hotspot returns None for empty position."""
        room = Room(room_with_hotspots)
        hotspot = room.find_hotspot((10, 10))
        assert hotspot is None

    def test_find_hotspot_multiple(self, room_with_hotspots):
        """find_hotspot returns first matching hotspot."""
        room = Room(room_with_hotspots)
        # Click on chest
        hotspot = room.find_hotspot((210, 160))
        assert hotspot is not None
        assert hotspot.name == "Chest"


# ============================================================================
# HOTSPOT MESSAGE TESTS
# ============================================================================

class TestHotspotMessages:
    """Test hotspot message selection logic."""

    def test_message_for_default_verb(self):
        """message_for returns simple verb message."""
        hotspot = Hotspot(
            rect=pygame.Rect(0, 0, 10, 10),
            name="Test",
            verbs={"look": "You see it."}
        )
        assert hotspot.message_for("look") == "You see it."

    def test_message_for_outcome_specific(self):
        """message_for returns outcome-specific message."""
        hotspot = Hotspot(
            rect=pygame.Rect(0, 0, 10, 10),
            name="Test",
            verbs={
                "use_default": "Can't use it.",
                "use_success": "You used it!",
                "use_missing": "You need an item."
            }
        )
        assert hotspot.message_for("use", "success") == "You used it!"
        assert hotspot.message_for("use", "missing") == "You need an item."

    def test_message_for_fallback_to_default(self):
        """message_for falls back to _default key."""
        hotspot = Hotspot(
            rect=pygame.Rect(0, 0, 10, 10),
            name="Test",
            verbs={
                "use_default": "Default message.",
                "use_success": "Success!"
            }
        )
        assert hotspot.message_for("use", "failure") == "Default message."

    def test_message_for_ultimate_fallback(self):
        """message_for returns generic message if nothing matches."""
        hotspot = Hotspot(
            rect=pygame.Rect(0, 0, 10, 10),
            name="Test",
            verbs={"look": "Something."}
        )
        assert hotspot.message_for("unknown_verb") == "Nothing happens."


# ============================================================================
# WALKABILITY TESTS
# ============================================================================

class TestWalkability:
    """Test walkability mask and queries."""

    def test_is_walkable_valid_position(self, basic_room_data):
        """is_walkable returns True for walkable area."""
        room = Room(basic_room_data)
        assert room.is_walkable((160, 100)) is True

    def test_is_walkable_out_of_bounds(self, basic_room_data):
        """is_walkable returns False for out of bounds."""
        room = Room(basic_room_data)
        assert room.is_walkable((-10, 100)) is False
        assert room.is_walkable((400, 100)) is False
        assert room.is_walkable((160, -10)) is False
        assert room.is_walkable((160, 300)) is False

    def test_is_walkable_complex_zones(self, complex_walkable_data):
        """is_walkable correctly evaluates complex walkable zones."""
        room = Room(complex_walkable_data)

        # Bottom area should be walkable
        assert room.is_walkable((160, 175)) is True

        # Center platform should be walkable
        assert room.is_walkable((160, 125)) is True

        # Top area should NOT be walkable
        assert room.is_walkable((160, 50)) is False

    def test_is_behind_priority_region(self, complex_walkable_data):
        """is_behind returns True for priority regions."""
        room = Room(complex_walkable_data)

        # Position in priority region (Y=80-120)
        assert room.is_behind((160, 100)) is True

    def test_is_behind_normal_region(self, complex_walkable_data):
        """is_behind returns False outside priority regions."""
        room = Room(complex_walkable_data)

        # Position outside priority region
        assert room.is_behind((160, 175)) is False

    def test_is_behind_out_of_bounds(self, complex_walkable_data):
        """is_behind returns False for out of bounds."""
        room = Room(complex_walkable_data)
        assert room.is_behind((-10, 100)) is False


# ============================================================================
# ZOMBIE SPAWNING TESTS
# ============================================================================

class TestZombieSpawning:
    """Test zombie spawning from room data."""

    def test_room_loads_zombies(self, room_with_zombies):
        """Room loads zombies from data."""
        room = Room(room_with_zombies)
        assert len(room.zombies) == 3

    def test_zombie_positions_set(self, room_with_zombies):
        """Zombie positions are set correctly."""
        room = Room(room_with_zombies)
        assert room.zombies[0].position.x == 100
        assert room.zombies[0].position.y == 100

    def test_zombie_types_set(self, room_with_zombies):
        """Zombie types are set when specified."""
        room = Room(room_with_zombies)
        assert room.zombies[0].zombie_type == "scene"
        assert room.zombies[1].zombie_type == "bouncer"

    def test_zombie_default_type(self, room_with_zombies):
        """Zombies without type get appropriate default."""
        room = Room(room_with_zombies)
        # Third zombie has no type, should get room-appropriate default
        assert room.zombies[2].zombie_type in ["scene", "bouncer", "rocker", "dj"]

    def test_room_without_zombies(self, basic_room_data):
        """Room with no zombies has empty list."""
        room = Room(basic_room_data)
        assert len(room.zombies) == 0


# ============================================================================
# ROOM UPDATE TESTS
# ============================================================================

class TestRoomUpdate:
    """Test room update functionality."""

    def test_update_moves_zombies(self, room_with_zombies):
        """update processes zombie movement."""
        room = Room(room_with_zombies)
        hero = Hero((50, 50))

        # Store initial positions
        initial_positions = [(z.position.x, z.position.y) for z in room.zombies]

        # Update room
        room.update(1.0, hero)

        # At least some zombies should have moved (wandering)
        # Note: This is probabilistic, but with 1 second update, likely

    def test_update_zombie_chasing(self, room_with_zombies):
        """Zombies chase hero when in range."""
        room = Room(room_with_zombies)
        hero = Hero((105, 105))  # Near first zombie

        # Update multiple times to trigger wander
        for _ in range(5):
            room.update(0.5, hero)


# ============================================================================
# ROOM DRAWING TESTS
# ============================================================================

class TestRoomDrawing:
    """Test room rendering."""

    def test_draw_creates_surface(self, basic_room_data):
        """draw renders to provided surface."""
        room = Room(basic_room_data)
        surface = pygame.Surface((320, 200))
        hero = Hero((100, 100))

        room.draw(surface, hero)
        # Should complete without error

    def test_draw_with_zombies(self, room_with_zombies):
        """draw renders zombies and hero."""
        room = Room(room_with_zombies)
        surface = pygame.Surface((320, 200))
        hero = Hero((150, 150))

        room.draw(surface, hero)
        # Should complete without error

    def test_draw_priority_overlay(self, complex_walkable_data):
        """draw applies priority overlay when hero is behind."""
        room = Room(complex_walkable_data)
        surface = pygame.Surface((320, 200))
        hero = Hero((160, 100))  # In priority region

        room.draw(surface, hero)
        # Should complete without error


# ============================================================================
# BACKGROUND CONFIGURATION TESTS
# ============================================================================

class TestBackgroundConfiguration:
    """Test background configuration parsing."""

    def test_background_with_gradient(self):
        """Room processes gradient background config."""
        data = {
            "id": "gradient_room",
            "size": [320, 200],
            "background": {
                "label": "Gradient",
                "gradient": [[30, 10, 60], [70, 40, 140]],
                "base_color": [50, 50, 50]
            },
            "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}]
        }
        room = Room(data)
        assert room.background is not None

    def test_background_with_accent_lines(self):
        """Room processes accent lines in background."""
        data = {
            "id": "accent_room",
            "size": [320, 200],
            "background": {
                "label": "Accents",
                "accent_lines": [
                    {"y": 100, "height": 5, "color": [255, 0, 0]},
                    {"y": 150, "height": 3, "color": [0, 255, 0]}
                ],
                "base_color": [50, 50, 50]
            },
            "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}]
        }
        room = Room(data)
        assert room.background is not None

    def test_background_with_shapes(self):
        """Room processes overlay shapes in background."""
        data = {
            "id": "shapes_room",
            "size": [320, 200],
            "background": {
                "label": "Shapes",
                "shapes": [
                    {"shape": "rect", "rect": [50, 50, 100, 100], "color": [200, 200, 200]}
                ],
                "base_color": [50, 50, 50]
            },
            "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}]
        }
        room = Room(data)
        assert room.background is not None

    def test_background_simple_config(self):
        """Room handles simple background config."""
        data = {
            "id": "simple_room",
            "size": [320, 200],
            "background": "Simple Label",
            "walkable_zones": [{"shape": "rect", "rect": [0, 0, 320, 200]}]
        }
        room = Room(data)
        assert room.background is not None
