"""Inventory data model for Zombie Quest."""

from __future__ import annotations

from typing import Dict, List, Optional

from items import Item


class Inventory:
    def __init__(self) -> None:
        self.items: List[Item] = []
        self.selected_item: Optional[Item] = None

    def add_item(self, item: Item) -> bool:
        if item not in self.items:
            self.items.append(item)
            return True
        return False

    def remove_item(self, name: str) -> Optional[Item]:
        for index, item in enumerate(self.items):
            if item.name == name:
                removed = self.items.pop(index)
                if self.selected_item == removed:
                    self.selected_item = None
                return removed
        return None

    def has_item(self, name: str) -> bool:
        return any(item.name == name for item in self.items)

    def select_item_by_index(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self.items):
            self.selected_item = self.items[index]
        else:
            self.selected_item = None
        return self.selected_item

    def select_item(self, item: Optional[Item]) -> None:
        self.selected_item = item

    def clear_selection(self) -> None:
        self.selected_item = None

    def to_serializable(self) -> List[Dict[str, str]]:
        return [{"name": item.name, "description": item.description} for item in self.items]
