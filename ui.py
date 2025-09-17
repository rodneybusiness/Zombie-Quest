"""User interface elements for the SCI-inspired Zombie Quest."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterable, List, Optional, Tuple

import pygame

import assets

Color = Tuple[int, int, int]


class Verb(Enum):
    WALK = auto()
    LOOK = auto()
    USE = auto()
    TALK = auto()


@dataclass
class Item:
    item_id: str
    name: str
    description: str
    icon_color: Color


@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)

    def add_item(self, item: Item) -> bool:
        self.items.append(item)
        return True

    def remove_item(self, item_id: str) -> Optional[Item]:
        for index, item in enumerate(self.items):
            if item.item_id == item_id:
                return self.items.pop(index)
        return None

    def has_item(self, item_id: str) -> bool:
        return any(item.item_id == item_id for item in self.items)

    def get_item(self, item_id: str) -> Optional[Item]:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None


@dataclass
class VerbIcon:
    verb: Verb
    surface: pygame.Surface
    rect: pygame.Rect


class VerbBar:
    def __init__(self, width: int, verbs: Iterable[Verb]) -> None:
        verbs = list(verbs)
        self.width = width
        self.height = 40
        self.background_color = assets.VGA_COLORS["ui_bar"]
        self.border_color = assets.VGA_COLORS["ui_accent"]
        self.icons: List[VerbIcon] = []
        padding = 6
        x = padding
        for verb in verbs:
            icon_surface = assets.get_ui_icon(verb.name.title(), (36, 30))
            rect = icon_surface.get_rect()
            rect.topleft = (x, 5)
            self.icons.append(VerbIcon(verb, icon_surface, rect))
            x += rect.width + padding
        self.inventory_icon = assets.get_ui_icon("Bag", (36, 30))
        self.inventory_rect = self.inventory_icon.get_rect()
        self.inventory_rect.topright = (self.width - 90, 5)
        self.options_icon = assets.get_ui_icon("Opt", (36, 30))
        self.options_rect = self.options_icon.get_rect()
        self.options_rect.topright = (self.width - 40, 5)
        self.cursor_surfaces: Dict[Verb, pygame.Surface] = {
            icon.verb: pygame.transform.smoothscale(icon.surface, (20, 20)) for icon in self.icons
        }

    def draw(self, surface: pygame.Surface, selected: Verb, selected_item: Optional[Item]) -> None:
        bar_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(surface, self.background_color, bar_rect)
        pygame.draw.rect(surface, self.border_color, bar_rect, 2)
        for icon in self.icons:
            surface.blit(icon.surface, icon.rect)
            if icon.verb == selected:
                pygame.draw.rect(surface, (255, 255, 255), icon.rect, 2)
        surface.blit(self.inventory_icon, self.inventory_rect)
        surface.blit(self.options_icon, self.options_rect)

        if selected_item is not None:
            font = assets.get_font(14)
            text = font.render(f"Item: {selected_item.name}", True, assets.VGA_COLORS["ui_accent"])
            surface.blit(text, (self.inventory_rect.right + 6, 12))

    def handle_click(self, position: Tuple[int, int]) -> Optional[Tuple[str, object]]:
        for icon in self.icons:
            if icon.rect.collidepoint(position):
                return ("verb", icon.verb)
        if self.inventory_rect.collidepoint(position):
            return ("inventory", None)
        if self.options_rect.collidepoint(position):
            return ("options", None)
        return None

    def get_cursor_surface(self, verb: Verb) -> pygame.Surface:
        return self.cursor_surfaces.get(verb, self.icons[0].surface)


class InventoryWindow:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.visible = False
        self.columns = 4
        self.cell_size = (56, 56)
        self.padding = 12
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.center = (assets.VGA_WIDTH // 2, assets.VGA_HEIGHT // 2)

    def toggle(self) -> None:
        self.visible = not self.visible

    def hide(self) -> None:
        self.visible = False

    def draw(self, screen: pygame.Surface, inventory: Inventory, selected_item_id: Optional[str]) -> None:
        if not self.visible:
            return
        self.surface.fill((*assets.VGA_COLORS["inventory_bg"], 220))
        pygame.draw.rect(self.surface, assets.VGA_COLORS["ui_accent"], self.surface.get_rect(), 2)

        font = assets.get_font(16)
        title = font.render("Inventory", True, assets.VGA_COLORS["ui_accent"])
        self.surface.blit(title, (16, 10))

        start_x = 16
        start_y = 40
        for index, item in enumerate(inventory.items):
            col = index % self.columns
            row = index // self.columns
            cell_rect = pygame.Rect(
                start_x + col * (self.cell_size[0] + self.padding),
                start_y + row * (self.cell_size[1] + self.padding),
                self.cell_size[0],
                self.cell_size[1],
            )
            pygame.draw.rect(self.surface, item.icon_color, cell_rect)
            pygame.draw.rect(self.surface, (0, 0, 0), cell_rect, 2)
            if item.item_id == selected_item_id:
                pygame.draw.rect(self.surface, (255, 255, 255), cell_rect, 2)
            item_font = assets.get_font(12)
            text = item_font.render(item.name[:8], True, (0, 0, 0))
            text_rect = text.get_rect(center=cell_rect.center)
            self.surface.blit(text, text_rect)
        screen.blit(self.surface, self.rect)

    def handle_click(self, position: Tuple[int, int], inventory: Inventory) -> Optional[str]:
        if not self.visible:
            return None
        if not self.rect.collidepoint(position):
            self.hide()
            return None
        local_x = position[0] - self.rect.left
        local_y = position[1] - self.rect.top
        start_x = 16
        start_y = 40
        for index, item in enumerate(inventory.items):
            col = index % self.columns
            row = index // self.columns
            cell_rect = pygame.Rect(
                start_x + col * (self.cell_size[0] + self.padding),
                start_y + row * (self.cell_size[1] + self.padding),
                self.cell_size[0],
                self.cell_size[1],
            )
            if cell_rect.collidepoint((local_x, local_y)):
                return item.item_id
        return None


class MessageWindow:
    def __init__(self, width: int) -> None:
        self.width = width
        self.height = 40
        self.background = pygame.Surface((width, self.height))
        self.background.fill((20, 20, 32))
        pygame.draw.rect(self.background, assets.VGA_COLORS["ui_accent"], self.background.get_rect(), 2)
        self.message = ""
        self.visible = False
        self.timer = 0.0
        self.duration = 4.0

    def show(self, text: str, duration: float = 4.0) -> None:
        self.message = text
        self.visible = True
        self.timer = 0.0
        self.duration = duration

    def update(self, dt: float) -> None:
        if not self.visible:
            return
        self.timer += dt
        if self.timer >= self.duration:
            self.visible = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        surface.blit(self.background, (0, assets.VGA_HEIGHT - self.height))
        font = assets.get_font(16)
        text_surface = font.render(self.message, True, assets.VGA_COLORS["ui_accent"])
        text_rect = text_surface.get_rect(center=(self.width // 2, assets.VGA_HEIGHT - self.height // 2))
        surface.blit(text_surface, text_rect)
