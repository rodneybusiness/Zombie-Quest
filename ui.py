"""User interface components for the Zombie Quest SCI-style engine."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

import assets
from inventory import Inventory
from items import Item
from settings import (
    MESSAGE_BAR_HEIGHT,
    MESSAGE_LINE_SPACING,
    MESSAGE_MAX_DURATION,
    MESSAGE_MIN_DURATION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TYPEWRITER_SPEED,
    UI_BAR_HEIGHT,
    VERBS,
)


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

    def _draw_panel(self, screen: pygame.Surface) -> None:
        gradient_top = pygame.Color(28, 34, 64)
        gradient_bottom = pygame.Color(66, 80, 128)
        for y in range(self.rect.height):
            t = y / max(1, self.rect.height - 1)
            color = (
                int(gradient_top.r + (gradient_bottom.r - gradient_top.r) * t),
                int(gradient_top.g + (gradient_bottom.g - gradient_top.g) * t),
                int(gradient_top.b + (gradient_bottom.b - gradient_top.b) * t),
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        pygame.draw.line(screen, (200, 200, 220), (0, 0), (SCREEN_WIDTH, 0), 2)
        pygame.draw.line(screen, (12, 12, 24), (0, self.rect.bottom - 1), (SCREEN_WIDTH, self.rect.bottom - 1), 2)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

    def draw(self, screen: pygame.Surface, current_verb: str, selected_item: Optional[Item]) -> None:
        self._draw_panel(screen)

        for icon in self.icons:
            drop_shadow = icon.rect.move(2, 3)
            shadow_surface = pygame.Surface(icon.rect.size, pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 90))
            screen.blit(shadow_surface, drop_shadow)
            screen.blit(icon.surface, icon.rect)
            if icon.verb == current_verb:
                pygame.draw.rect(screen, (255, 230, 120), icon.rect.inflate(6, 6), 3)

        screen.blit(self.inventory_icon, self.inventory_rect)
        screen.blit(self.options_icon, self.options_rect)
        if selected_item:
            font = assets.get_font("timesnewroman", 18)
            label = font.render(f"Selected: {selected_item.name}", True, (255, 240, 220))
            outline = font.render(f"Selected: {selected_item.name}", True, (16, 16, 16))
            label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, self.rect.bottom - 20))
            screen.blit(outline, label_rect.move(1, 1))
            screen.blit(label, label_rect)

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

    def _draw_panel(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, (12, 16, 26), self.rect.inflate(8, 8))
        panel = pygame.Surface(self.rect.size)
        for y in range(self.rect.height):
            t = y / max(1, self.rect.height - 1)
            color = (
                int(36 + 40 * t),
                int(48 + 32 * t),
                int(68 + 28 * t),
            )
            pygame.draw.line(panel, color, (0, y), (self.rect.width, y))
        checker = pygame.Surface((8, 8))
        checker.fill((60, 78, 104))
        pygame.draw.rect(checker, (42, 58, 84), (0, 0, 4, 4))
        pygame.draw.rect(checker, (42, 58, 84), (4, 4, 4, 4))
        for x in range(0, self.rect.width, 8):
            for y in range(0, self.rect.height, 8):
                panel.blit(checker, (x, y))
        screen.blit(panel, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

    def draw(self, screen: pygame.Surface, inventory: Inventory) -> None:
        if not self.visible:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        self._draw_panel(screen)
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
        self._queue: deque[Tuple[str, float]] = deque()
        self._current: Optional[Tuple[str, float]] = None
        self.timer = 0.0
        self.revealed = 0
        self.visible = False

    def show_message(self, text: str, duration: float = 4.0) -> None:
        self.push_message(text, duration)

    def push_message(self, text: str, duration: float | None = None) -> None:
        text = text.strip()
        if not text:
            return
        if duration is None:
            estimated = max(len(text) / TYPEWRITER_SPEED + 1.2, MESSAGE_MIN_DURATION)
            duration = min(estimated, MESSAGE_MAX_DURATION)
        self._queue.append((text, float(duration)))
        if not self._current:
            self._advance_queue()

    def push_messages(self, lines: List[str]) -> None:
        for line in lines:
            self.push_message(line)

    def clear(self) -> None:
        self._queue.clear()
        self._current = None
        self.visible = False
        self.timer = 0.0
        self.revealed = 0

    def _advance_queue(self) -> None:
        if self._queue:
            self._current = self._queue.popleft()
            self.timer = 0.0
            self.revealed = 0
            self.visible = True
        else:
            self._current = None
            self.visible = False

    def update(self, dt: float) -> None:
        if not self._current:
            if self._queue:
                self._advance_queue()
            return
        text, duration = self._current
        self.timer += dt
        self.revealed = min(len(text), int(self.timer * TYPEWRITER_SPEED))
        if self.timer >= duration:
            self._advance_queue()

    def draw(self, screen: pygame.Surface) -> None:
        panel = pygame.Surface(self.rect.size)
        for y in range(self.rect.height):
            t = y / max(1, self.rect.height - 1)
            color = (
                int(20 + 28 * t),
                int(28 + 40 * t),
                int(48 + 56 * t),
            )
            pygame.draw.line(panel, color, (0, y), (self.rect.width, y))
        screen.blit(panel, self.rect.topleft)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        if not self.visible or not self._current:
            return
        font = assets.get_font("timesnewroman", 18)
        text, _ = self._current
        visible_text = text[: self.revealed]
        wrapped = wrap_text(visible_text, font, self.rect.width - 24)
        y = self.rect.y + 10
        for line in wrapped:
            text = font.render(line, True, (245, 245, 200))
            outline = font.render(line, True, (10, 10, 16))
            screen.blit(outline, (self.rect.x + 14, y + 2))
            screen.blit(text, (self.rect.x + 12, y))
            y += text.get_height() + MESSAGE_LINE_SPACING


class CursorManager:
    def __init__(self) -> None:
        pygame.mouse.set_visible(False)

    def draw(self, screen: pygame.Surface, verb: str, selected_item: Optional[Item]) -> None:
        pos = pygame.mouse.get_pos()
        icon = assets.get_cursor_icon(verb)
        shadow = icon.copy()
        shadow.fill((0, 0, 0, 140), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
        screen.blit(icon, pos)
        font = assets.get_font("timesnewroman", 14)
        verb_label = font.render(verb.title(), True, (255, 250, 224))
        outline = font.render(verb.title(), True, (16, 8, 24))
        label_pos = (pos[0] + icon.get_width() + 8, pos[1] + 4)
        screen.blit(outline, (label_pos[0] + 1, label_pos[1] + 1))
        screen.blit(verb_label, label_pos)
        if selected_item:
            font = assets.get_font("timesnewroman", 16)
            text = font.render(selected_item.name, True, (255, 255, 255))
            screen.blit(text, (label_pos[0], label_pos[1] + verb_label.get_height() + 2))


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
