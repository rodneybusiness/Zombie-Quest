"""Tests for save/load system."""
import pytest
import os
import tempfile

from zombie_quest.save_system import SaveData, SaveManager


class TestSaveData:
    """Test save data structure."""

    def test_save_data_creation(self):
        data = SaveData(
            current_room="test_room",
            hero_position=(100.0, 100.0),
            inventory_items=["Key", "Map"],
            flags={"talked_to_npc": True},
        )
        assert data.current_room == "test_room"
        assert data.hero_position == (100.0, 100.0)
        assert "Key" in data.inventory_items

    def test_save_data_defaults(self):
        data = SaveData()
        assert data.current_room == "hennepin_outside"
        assert data.hero_health == 3
        assert data.inventory_items == []

    def test_save_data_to_dict(self):
        data = SaveData(
            current_room="test_room",
            hero_position=(100.0, 100.0),
            inventory_items=[],
            flags={},
        )
        d = data.to_dict()
        assert isinstance(d, dict)
        assert d["current_room"] == "test_room"
        assert d["hero_position"] == [100.0, 100.0]  # Converted to list

    def test_save_data_from_dict(self):
        d = {
            "current_room": "test_room",
            "hero_position": [100.0, 100.0],
            "hero_health": 3,
            "inventory_items": ["Key"],
            "flags": {"flag1": True},
            "save_name": "Test",
            "save_time": "2024-01-01T00:00:00",
            "play_time": 0.0,
            "version": "1.0.0",
            "selected_item": None,
            "hotspot_states": {},
            "zombies_encountered": 0,
            "items_collected": 0,
            "rooms_visited": [],
        }
        data = SaveData.from_dict(d)
        assert data.current_room == "test_room"
        assert data.hero_position == (100.0, 100.0)
        assert data.hero_health == 3


class TestSaveManager:
    """Test save file management."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for saves."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_save_and_load(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)
        data = SaveData(
            current_room="test_room",
            hero_position=(50.0, 50.0),
            inventory_items=["Flyer"],
            flags={"tested": True},
        )

        # Save
        result = manager.save_game(data, slot_name="test_slot")
        assert result is True

        # Load
        loaded = manager.load_game(slot_name="test_slot")
        assert loaded is not None
        assert loaded.current_room == "test_room"
        assert loaded.hero_position == (50.0, 50.0)
        assert "Flyer" in loaded.inventory_items

    def test_list_saves(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)

        # Initially empty
        saves = manager.list_saves()
        assert len(saves) == 0

        # Add a save
        data = SaveData(
            current_room="room1",
            hero_position=(0.0, 0.0),
            inventory_items=[],
            flags={},
        )
        manager.save_game(data, slot_name="slot1")

        saves = manager.list_saves()
        assert len(saves) == 1

    def test_delete_save(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)
        data = SaveData(
            current_room="room1",
            hero_position=(0.0, 0.0),
            inventory_items=[],
            flags={},
        )
        manager.save_game(data, slot_name="slot1")

        result = manager.delete_save(slot_name="slot1")
        assert result is True

        saves = manager.list_saves()
        assert len(saves) == 0

    def test_load_nonexistent(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)
        loaded = manager.load_game(slot_name="nonexistent999")
        assert loaded is None

    def test_has_save(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)
        assert manager.has_save("test") is False

        manager.save_game(SaveData(), slot_name="test")
        assert manager.has_save("test") is True

    def test_autosave(self, temp_save_dir):
        manager = SaveManager(save_directory=temp_save_dir)
        data = SaveData()
        result = manager.autosave(data)
        assert result is True
        assert manager.has_save(manager.autosave_slot) is True
