"""Item definitions used by the inventory and hotspot system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame

import assets


@dataclass
class ItemDefinition:
    name: str
    description: str
    icon_color: Tuple[int, int, int]

    def create_instance(self) -> "Item":
        return Item(self.name, self.description, self.icon_color)


class Item:
    def __init__(self, name: str, description: str, icon_color: Tuple[int, int, int]):
        self.name = name
        self.description = description
        self.icon_color = icon_color
        self.icon_surface = assets.create_inventory_icon(name, pygame.Color(*icon_color))

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Item(name={self.name!r})"
