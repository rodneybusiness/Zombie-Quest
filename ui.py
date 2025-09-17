"""User interface components for the Zombie Quest SCI-style engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

import assets
from inventory import Inventory
from items import Item
from settings import MESSAGE_BAR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, UI_BAR_HEIGHT, VERBS


@dataclass
class VerbIcon:
    verb: str
    surface: pygame.Surface
    rect: pygame.Rect


class VerbBar:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_BAR_HEIGHT)
        self.icons: List[VerbIcon] = []
        self.inventory_icon = assets.create_ui_icon("Bag", (56, 56), pygame.Color(160, 120, 80))
        self.options_icon = assets.create_ui_icon("Opt", (56, 56), pygame.Color(120, 120, 160))
        self.inventory_rect = pygame.Rect(SCREEN_WIDTH - 128, 8, 56, 56)
        self.options_rect = pygame.Rect(SCREEN_WIDTH - 64, 8, 56, 56)
        self._build_icons()

    def _build_icons(self) -> None:
        x = 12
        for verb in VERBS:
            icon_surface = assets.create_ui_icon(verb.title(), (56, 56), pygame.Color(80, 110, 140))
            rect = pygame.Rect(x, 8, 56, 56)
            self.icons.append(VerbIcon(verb, icon_surface, rect))
            x += 60

    def draw(self, screen: pygame.Surface, current_verb: str, selected_item: Optional[Item]) -> None:
        # Draw background gradient reminiscent of SCI UI bars.
        for y in range(self.rect.height):
            color_value = 40 + int(20 * (y / self.rect.height))
            pygame.draw.line(screen, (color_value, color_value + 10, color_value + 40), (0, y), (SCREEN_WIDTH, y))
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        for icon in self.icons:
            screen.blit(icon.surface, icon.rect)
            if icon.verb == current_verb:
                pygame.draw.rect(screen, (255, 255, 0), icon.rect, 3)

        screen.blit(self.inventory_icon, self.inventory_rect)
        screen.blit(self.options_icon, self.options_rect)
        if selected_item:
            font = assets.get_font("timesnewroman", 18)
            label = font.render(f"Selected: {selected_item.name}", True, (255, 255, 255))
            screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, UI_BAR_HEIGHT - label.get_height() - 6))

    def handle_click(self, pos: Tuple[int, int]) -> Optional[Dict[str, str]]:
        if not self.rect.collidepoint(pos):
            return None
        for icon in self.icons:
            if icon.rect.collidepoint(pos):
                return {"verb": icon.verb}
        if self.inventory_rect.collidepoint(pos):
            return {"inventory": "toggle"}
        if self.options_rect.collidepoint(pos):
            return {"options": "open"}
        return None


class InventoryWindow:
    def __init__(self) -> None:
        self.visible = False
        width = SCREEN_WIDTH // 2
        height = SCREEN_HEIGHT // 2
        self.rect = pygame.Rect((SCREEN_WIDTH - width) // 2, (SCREEN_HEIGHT - height) // 2, width, height)
        self.columns = 4
        self.cell_size = 72
        self.padding = 16

    def toggle(self) -> None:
        self.visible = not self.visible

    def hide(self) -> None:
        self.visible = False

    def draw(self, screen: pygame.Surface, inventory: Inventory) -> None:
        if not self.visible:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (40, 56, 80), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        font = assets.get_font("timesnewroman", 20)
        title = font.render("Inventory", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + (self.rect.width - title.get_width()) // 2, self.rect.y + 8))

        start_x = self.rect.x + self.padding
        start_y = self.rect.y + 48
        for index, item in enumerate(inventory.items):
            col = index % self.columns
            row = index // self.columns
            item_rect = pygame.Rect(
                start_x + col * self.cell_size,
                start_y + row * self.cell_size,
                self.cell_size - 8,
                self.cell_size - 8,
            )
            screen.blit(item.icon_surface, item_rect)
            if inventory.selected_item == item:
                pygame.draw.rect(screen, (255, 255, 0), item_rect, 3)

        if inventory.selected_item:
            desc_font = assets.get_font("timesnewroman", 16)
            wrapped = wrap_text(inventory.selected_item.description, desc_font, self.rect.width - 32)
            y = self.rect.bottom - 80
            for line in wrapped:
                text = desc_font.render(line, True, (220, 220, 220))
                screen.blit(text, (self.rect.x + 16, y))
                y += text.get_height() + 4

    def handle_click(self, pos: Tuple[int, int], inventory: Inventory) -> Optional[Item]:
        if not self.visible or not self.rect.collidepoint(pos):
            return None
        start_x = self.rect.x + self.padding
        start_y = self.rect.y + 48
        for index, item in enumerate(inventory.items):
            col = index % self.columns
            row = index // self.columns
            item_rect = pygame.Rect(
                start_x + col * self.cell_size,
                start_y + row * self.cell_size,
                self.cell_size - 8,
                self.cell_size - 8,
            )
            if item_rect.collidepoint(pos):
                inventory.select_item(item)
                return item
        return None


class MessageBar:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, SCREEN_HEIGHT - MESSAGE_BAR_HEIGHT, SCREEN_WIDTH, MESSAGE_BAR_HEIGHT)
        self.message = ""
        self.timer = 0.0
        self.duration = 4.0
        self.visible = False

    def show_message(self, text: str, duration: float = 4.0) -> None:
        self.message = text
        self.timer = 0.0
        self.duration = duration
        self.visible = True

    def update(self, dt: float) -> None:
        if not self.visible:
            return
        self.timer += dt
        if self.timer >= self.duration:
            self.visible = False

    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
        pygame.draw.rect(screen, (24, 36, 56), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        font = assets.get_font("timesnewroman", 18)
        wrapped = wrap_text(self.message, font, self.rect.width - 16)
        y = self.rect.y + 8
        for line in wrapped:
            text = font.render(line, True, (245, 245, 200))
            screen.blit(text, (self.rect.x + 12, y))
            y += text.get_height() + 2


class CursorManager:
    def __init__(self) -> None:
        pygame.mouse.set_visible(False)

    def draw(self, screen: pygame.Surface, verb: str, selected_item: Optional[Item]) -> None:
        pos = pygame.mouse.get_pos()
        icon = assets.get_cursor_icon(verb)
        screen.blit(icon, pos)
        if selected_item:
            font = assets.get_font("timesnewroman", 16)
            text = font.render(selected_item.name, True, (255, 255, 255))
            screen.blit(text, (pos[0] + icon.get_width() + 4, pos[1]))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        tentative = f"{current} {word}".strip()
        if font.size(tentative)[0] <= max_width:
            current = tentative
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
