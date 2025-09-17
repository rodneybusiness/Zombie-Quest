from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame

from .resources import create_ui_icon, load_serif_font

Color = Tuple[int, int, int]


class Verb(Enum):
    WALK = "walk"
    LOOK = "look"
    USE = "use"
    TALK = "talk"

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.value


VERB_COLORS: Dict[Verb, Color] = {
    Verb.WALK: (70, 160, 220),
    Verb.LOOK: (220, 200, 70),
    Verb.USE: (120, 200, 120),
    Verb.TALK: (220, 120, 160),
}


@dataclass
class Item:
    name: str
    description: str
    icon_color: Color


class Inventory:
    def __init__(self) -> None:
        self.items: List[Item] = []
        self.selected_item: Optional[Item] = None

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, name: str) -> Optional[Item]:
        for index, item in enumerate(self.items):
            if item.name == name:
                removed = self.items.pop(index)
                if self.selected_item and self.selected_item.name == name:
                    self.selected_item = None
                return removed
        return None

    def has_item(self, name: str) -> bool:
        return any(item.name == name for item in self.items)

    def select_item(self, item: Optional[Item]) -> None:
        self.selected_item = item


class MessageBox:
    def __init__(self, width: int, height: int) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.font = load_serif_font(16)
        self.message = ""
        self.duration = 4.0
        self.timer = 0.0

    def show(self, message: str) -> None:
        self.message = message
        self.timer = self.duration

    def update(self, dt: float) -> None:
        if self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.message = ""

    def draw(self, surface: pygame.Surface) -> None:
        if not self.message:
            return
        pygame.draw.rect(surface, (20, 20, 40), self.rect)
        pygame.draw.rect(surface, (200, 200, 220), self.rect, 2)
        text_surface = self.font.render(self.message, True, (230, 230, 240))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class VerbBar:
    def __init__(self, width: int, height: int) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.selected_verb = Verb.WALK
        self.font = load_serif_font(12)
        self.verb_icons: List[Tuple[Verb, pygame.Surface, pygame.Rect]] = []
        icon_size = (32, 32)
        padding = 6
        x = padding
        for verb in (Verb.WALK, Verb.LOOK, Verb.USE, Verb.TALK):
            surface = create_ui_icon(verb.value.title(), icon_size, VERB_COLORS[verb])
            rect = surface.get_rect(topleft=(x, (height - icon_size[1]) // 2))
            self.verb_icons.append((verb, surface, rect))
            x += icon_size[0] + padding
        self.inventory_icon = create_ui_icon("Inventory", icon_size, (160, 110, 200))
        self.inventory_rect = self.inventory_icon.get_rect(
            topleft=(width - icon_size[0] * 2 - padding * 2, (height - icon_size[1]) // 2)
        )
        self.options_icon = create_ui_icon("Options", icon_size, (110, 160, 200))
        self.options_rect = self.options_icon.get_rect(topleft=(width - icon_size[0] - padding, (height - icon_size[1]) // 2))

    def draw(self, surface: pygame.Surface) -> None:
        gradient = pygame.Surface(self.rect.size)
        for y in range(self.rect.height):
            ratio = y / max(1, self.rect.height - 1)
            color = (
                int(25 + 40 * ratio),
                int(35 + 60 * ratio),
                int(60 + 80 * ratio),
            )
            pygame.draw.line(gradient, color, (0, y), (self.rect.width, y))
        surface.blit(gradient, self.rect)
        pygame.draw.rect(surface, (180, 180, 200), self.rect, 2)
        for verb, icon_surface, icon_rect in self.verb_icons:
            surface.blit(icon_surface, icon_rect)
            if verb == self.selected_verb:
                pygame.draw.rect(surface, (255, 255, 255), icon_rect, 2)
        surface.blit(self.inventory_icon, self.inventory_rect)
        surface.blit(self.options_icon, self.options_rect)

    def handle_click(self, position: Tuple[int, int]) -> Optional[str]:
        for verb, _, rect in self.verb_icons:
            if rect.collidepoint(position):
                self.selected_verb = verb
                return "verb"
        if self.inventory_rect.collidepoint(position):
            return "inventory"
        if self.options_rect.collidepoint(position):
            return "options"
        return None

    def cycle_next(self) -> Verb:
        verbs = [icon[0] for icon in self.verb_icons]
        index = verbs.index(self.selected_verb)
        self.selected_verb = verbs[(index + 1) % len(verbs)]
        return self.selected_verb


class InventoryWindow:
    def __init__(self, inventory: Inventory, rect: pygame.Rect) -> None:
        self.inventory = inventory
        self.rect = rect
        self.visible = False
        self.font = load_serif_font(12)
        self.item_rects: List[Tuple[Item, pygame.Rect]] = []

    def toggle(self) -> None:
        self.visible = not self.visible
        if not self.visible:
            self.inventory.select_item(None)

    def close(self) -> None:
        self.visible = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        pygame.draw.rect(surface, (30, 30, 60), self.rect)
        pygame.draw.rect(surface, (200, 200, 220), self.rect, 2)
        padding = 8
        columns = 4
        icon_size = 40
        self.item_rects = []
        for index, item in enumerate(self.inventory.items):
            row = index // columns
            column = index % columns
            x = self.rect.x + padding + column * (icon_size + padding)
            y = self.rect.y + padding + row * (icon_size + padding)
            icon_rect = pygame.Rect(x, y, icon_size, icon_size)
            pygame.draw.rect(surface, item.icon_color, icon_rect)
            pygame.draw.rect(surface, (20, 20, 20), icon_rect, 2)
            label_surface = self.font.render(item.name, True, (230, 230, 240))
            label_rect = label_surface.get_rect(midtop=(icon_rect.centerx, icon_rect.bottom + 2))
            surface.blit(label_surface, label_rect)
            if self.inventory.selected_item and self.inventory.selected_item.name == item.name:
                pygame.draw.rect(surface, (255, 255, 0), icon_rect, 3)
            self.item_rects.append((item, icon_rect))

    def handle_event(self, event: pygame.event.Event) -> Optional[Item]:
        if not self.visible:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                self.toggle()
            else:
                for item, rect in self.item_rects:
                    if rect.collidepoint(event.pos):
                        if self.inventory.selected_item and self.inventory.selected_item.name == item.name:
                            self.inventory.select_item(None)
                        else:
                            self.inventory.select_item(item)
                        return item
        return None
