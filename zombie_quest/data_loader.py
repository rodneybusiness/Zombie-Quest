from __future__ import annotations

import json
import os
from typing import Dict, List

from .rooms import Room
from .ui import Item


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_game_data(base_path: str, filename: str = "game_data.json") -> Dict:
    full_path = os.path.join(base_path, filename)
    return load_json(full_path)


def build_rooms(room_data: List[Dict]) -> Dict[str, Room]:
    rooms: Dict[str, Room] = {}
    for data in room_data:
        room = Room(data)
        rooms[room.id] = room
    return rooms


def build_items(items_data: List[Dict]) -> Dict[str, Item]:
    items: Dict[str, Item] = {}
    for data in items_data:
        item = Item(
            name=data["name"],
            description=data.get("description", ""),
            icon_color=tuple(data.get("icon_color", [200, 200, 200])),
        )
        items[item.name] = item
    return items
