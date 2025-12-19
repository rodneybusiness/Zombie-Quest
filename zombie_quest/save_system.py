"""Save/Load system for game persistence."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class SaveData:
    """Represents a complete game save state."""
    # Meta
    save_name: str = "Autosave"
    save_time: str = field(default_factory=lambda: datetime.now().isoformat())
    play_time: float = 0.0
    version: str = "1.0.0"

    # Player state
    current_room: str = "hennepin_outside"
    hero_position: Tuple[float, float] = (72.0, 172.0)
    hero_health: int = 3

    # Inventory
    inventory_items: List[str] = field(default_factory=list)
    selected_item: Optional[str] = None

    # Story progress
    flags: Dict[str, bool] = field(default_factory=dict)

    # Hotspot states (which items have been taken, etc.)
    hotspot_states: Dict[str, Dict[str, bool]] = field(default_factory=dict)

    # Statistics
    zombies_encountered: int = 0
    items_collected: int = 0
    rooms_visited: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert tuple to list for JSON
        data['hero_position'] = list(self.hero_position)
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveData':
        """Create from dictionary."""
        # Convert position back to tuple
        if 'hero_position' in data:
            data['hero_position'] = tuple(data['hero_position'])
        return cls(**data)


class SaveManager:
    """Manages game saves and loads."""

    def __init__(self, save_directory: str = None) -> None:
        if save_directory is None:
            # Default to saves directory in game folder
            self.save_directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "saves"
            )
        else:
            self.save_directory = save_directory

        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)

        self.autosave_slot = "autosave"
        self.max_saves = 10

    def _get_save_path(self, slot_name: str) -> str:
        """Get the full path for a save slot."""
        safe_name = "".join(c for c in slot_name if c.isalnum() or c in "._-")
        return os.path.join(self.save_directory, f"{safe_name}.json")

    def save_game(self, save_data: SaveData, slot_name: str = None) -> bool:
        """Save the game to a slot. Returns True on success."""
        if slot_name is None:
            slot_name = self.autosave_slot

        save_data.save_time = datetime.now().isoformat()
        save_path = self._get_save_path(slot_name)

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False

    def load_game(self, slot_name: str = None) -> Optional[SaveData]:
        """Load a game from a slot. Returns None on failure."""
        if slot_name is None:
            slot_name = self.autosave_slot

        save_path = self._get_save_path(slot_name)

        if not os.path.exists(save_path):
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SaveData.from_dict(data)
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None

    def delete_save(self, slot_name: str) -> bool:
        """Delete a save slot. Returns True on success."""
        save_path = self._get_save_path(slot_name)

        if not os.path.exists(save_path):
            return False

        try:
            os.remove(save_path)
            return True
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False

    def list_saves(self) -> List[Tuple[str, SaveData]]:
        """List all available saves with their metadata."""
        saves = []

        if not os.path.exists(self.save_directory):
            return saves

        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                slot_name = filename[:-5]  # Remove .json
                save_data = self.load_game(slot_name)
                if save_data:
                    saves.append((slot_name, save_data))

        # Sort by save time, newest first
        saves.sort(key=lambda x: x[1].save_time, reverse=True)
        return saves

    def has_save(self, slot_name: str = None) -> bool:
        """Check if a save exists in the given slot."""
        if slot_name is None:
            slot_name = self.autosave_slot
        return os.path.exists(self._get_save_path(slot_name))

    def autosave(self, save_data: SaveData) -> bool:
        """Perform an autosave."""
        save_data.save_name = "Autosave"
        return self.save_game(save_data, self.autosave_slot)

    def create_new_game_save(self) -> SaveData:
        """Create a fresh save data for a new game."""
        return SaveData(
            save_name="New Game",
            current_room="hennepin_outside",
            hero_position=(72.0, 172.0),
            hero_health=3,
            inventory_items=[],
            flags={},
            rooms_visited=["hennepin_outside"]
        )


class GameStateSerializer:
    """Helper to serialize/deserialize game state to/from SaveData."""

    @staticmethod
    def capture_state(engine: 'GameEngine') -> SaveData:
        """Capture current game state into SaveData."""
        from .ui import Item

        save_data = SaveData()

        # Player state
        save_data.current_room = engine.current_room.id
        save_data.hero_position = (engine.hero.position.x, engine.hero.position.y)
        save_data.hero_health = getattr(engine.hero, 'health', 3)

        # Inventory
        save_data.inventory_items = [item.name for item in engine.inventory.items]
        if engine.inventory.selected_item:
            save_data.selected_item = engine.inventory.selected_item.name

        # Flags
        save_data.flags = dict(getattr(engine, 'game_flags', {}))

        # Hotspot states
        for room_id, room in engine.rooms.items():
            room_states = {}
            for hotspot in room.hotspots:
                if hotspot.give_item is None:  # Item was already taken
                    room_states[hotspot.name] = {"item_taken": True}
            if room_states:
                save_data.hotspot_states[room_id] = room_states

        # Statistics
        save_data.rooms_visited = list(getattr(engine, 'visited_rooms', [engine.current_room.id]))
        save_data.items_collected = len(save_data.inventory_items)

        return save_data

    @staticmethod
    def restore_state(engine: 'GameEngine', save_data: SaveData) -> None:
        """Restore game state from SaveData."""
        # Room and position
        if save_data.current_room in engine.rooms:
            engine.current_room = engine.rooms[save_data.current_room]
        engine.hero.position.x = save_data.hero_position[0]
        engine.hero.position.y = save_data.hero_position[1]
        engine.hero.path = []
        engine.hero.current_target = None

        # Health
        if hasattr(engine.hero, 'health'):
            engine.hero.health = save_data.hero_health

        # Inventory
        engine.inventory.items.clear()
        engine.inventory.selected_item = None
        for item_name in save_data.inventory_items:
            item = engine.items_catalog.get(item_name)
            if item:
                engine.inventory.add_item(item)
        if save_data.selected_item:
            for item in engine.inventory.items:
                if item.name == save_data.selected_item:
                    engine.inventory.select_item(item)
                    break

        # Flags
        if hasattr(engine, 'game_flags'):
            engine.game_flags.update(save_data.flags)
        else:
            engine.game_flags = dict(save_data.flags)

        # Hotspot states
        for room_id, room_states in save_data.hotspot_states.items():
            if room_id in engine.rooms:
                room = engine.rooms[room_id]
                for hotspot in room.hotspots:
                    if hotspot.name in room_states:
                        state = room_states[hotspot.name]
                        if state.get("item_taken"):
                            hotspot.give_item = None

        # Statistics
        if hasattr(engine, 'visited_rooms'):
            engine.visited_rooms = set(save_data.rooms_visited)
        else:
            engine.visited_rooms = set(save_data.rooms_visited)
