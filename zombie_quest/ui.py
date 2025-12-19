"""Enhanced UI system with beautiful graphics and full keyboard/mouse support.

Features:
- Stylized verb icons with hover effects
- Health display with heart icons
- Glowing neon UI elements
- Inventory with detailed item icons
- Message box with typewriter effect
- Full keyboard navigation
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame

from .config import COLORS, ANIMATION
from .resources import load_serif_font
from .sprites import create_verb_icon, create_heart_icon, create_detailed_item_icon

Color = Tuple[int, int, int]


class Verb(Enum):
    """Available interaction verbs."""
    WALK = "walk"
    LOOK = "look"
    USE = "use"
    TALK = "talk"

    def __str__(self) -> str:
        return self.value


VERB_COLORS: Dict[Verb, Color] = {
    Verb.WALK: COLORS.VERB_WALK,
    Verb.LOOK: COLORS.VERB_LOOK,
    Verb.USE: COLORS.VERB_USE,
    Verb.TALK: COLORS.VERB_TALK,
}

# Keyboard shortcuts for verbs
VERB_KEYS: Dict[int, Verb] = {
    pygame.K_1: Verb.WALK,
    pygame.K_2: Verb.LOOK,
    pygame.K_3: Verb.USE,
    pygame.K_4: Verb.TALK,
}


@dataclass
class Item:
    """Represents an inventory item."""
    name: str
    description: str
    icon_color: Color
    icon: Optional[pygame.Surface] = field(default=None, repr=False)

    def __post_init__(self):
        if self.icon is None:
            self.icon = create_detailed_item_icon(self.name, self.icon_color)


class Inventory:
    """Manages the player's inventory."""

    def __init__(self, max_items: int = 8) -> None:
        self.items: List[Item] = []
        self.selected_item: Optional[Item] = None
        self.max_items = max_items

    def add_item(self, item: Item) -> bool:
        """Add item to inventory. Returns False if inventory is full."""
        if len(self.items) >= self.max_items:
            return False
        # Create icon if needed
        if item.icon is None:
            item.icon = create_detailed_item_icon(item.name, item.icon_color)
        self.items.append(item)
        return True

    def remove_item(self, name: str) -> Optional[Item]:
        """Remove and return an item by name."""
        for index, item in enumerate(self.items):
            if item.name == name:
                removed = self.items.pop(index)
                if self.selected_item and self.selected_item.name == name:
                    self.selected_item = None
                return removed
        return None

    def has_item(self, name: str) -> bool:
        """Check if inventory contains an item."""
        return any(item.name == name for item in self.items)

    def select_item(self, item: Optional[Item]) -> None:
        """Select an item for use."""
        self.selected_item = item

    def get_item_names(self) -> List[str]:
        """Get list of item names."""
        return [item.name for item in self.items]


class MessageBox:
    """Displays game messages with typewriter effect."""

    def __init__(self, width: int, height: int) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.font = load_serif_font(16)
        self.full_message = ""
        self.displayed_message = ""
        self.duration = ANIMATION.MESSAGE_DISPLAY_TIME
        self.timer = 0.0
        self.char_timer = 0.0
        self.chars_per_second = 60
        self.is_typing = False

    def show(self, message: str) -> None:
        """Show a new message with typewriter effect."""
        self.full_message = message
        self.displayed_message = ""
        self.timer = self.duration
        self.char_timer = 0.0
        self.is_typing = True

    def skip_typing(self) -> None:
        """Skip to full message."""
        self.displayed_message = self.full_message
        self.is_typing = False

    def update(self, dt: float) -> None:
        """Update message display."""
        if self.is_typing:
            self.char_timer += dt * self.chars_per_second
            chars_to_show = int(self.char_timer)
            if chars_to_show >= len(self.full_message):
                self.displayed_message = self.full_message
                self.is_typing = False
            else:
                self.displayed_message = self.full_message[:chars_to_show]
        elif self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.full_message = ""
                self.displayed_message = ""

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the message box."""
        if not self.displayed_message:
            return

        # Background with glow effect
        box_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Dark background
        pygame.draw.rect(box_surface, (*COLORS.UI_DARK, 240), box_surface.get_rect())

        # Neon border
        pygame.draw.rect(box_surface, COLORS.UI_BORDER, box_surface.get_rect(), 2)

        # Inner glow
        inner_rect = pygame.Rect(2, 2, self.rect.width - 4, self.rect.height - 4)
        pygame.draw.rect(box_surface, (*COLORS.HOT_MAGENTA, 30), inner_rect, 1)

        # Text
        text_surface = self.font.render(self.displayed_message, True, COLORS.UI_TEXT)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        box_surface.blit(text_surface, text_rect)

        # Typing indicator
        if self.is_typing:
            cursor_x = text_rect.right + 2
            if int(self.char_timer * 2) % 2 == 0:
                pygame.draw.rect(box_surface, COLORS.UI_TEXT,
                               (min(cursor_x, self.rect.width - 10), text_rect.top, 2, text_rect.height))

        surface.blit(box_surface, self.rect)


class HealthDisplay:
    """Displays player health as heart icons."""

    def __init__(self, x: int, y: int, max_health: int = 3) -> None:
        self.x = x
        self.y = y
        self.max_health = max_health
        self.heart_full = create_heart_icon(full=True)
        self.heart_empty = create_heart_icon(full=False)
        self.heart_spacing = 16

    def draw(self, surface: pygame.Surface, current_health: int) -> None:
        """Draw health hearts."""
        for i in range(self.max_health):
            heart = self.heart_full if i < current_health else self.heart_empty
            x = self.x + i * self.heart_spacing
            surface.blit(heart, (x, self.y))


class VerbBar:
    """The verb selection bar at the top of the screen."""

    def __init__(self, width: int, height: int) -> None:
        self.rect = pygame.Rect(0, 0, width, height)
        self.selected_verb = Verb.WALK
        self.hovered_verb: Optional[Verb] = None
        self.font = load_serif_font(10)

        # Create verb icons
        self.verb_icons: List[Tuple[Verb, pygame.Surface, pygame.Rect]] = []
        icon_size = (28, 28)
        padding = 6
        x = padding

        for verb in (Verb.WALK, Verb.LOOK, Verb.USE, Verb.TALK):
            icon = create_verb_icon(verb.value, icon_size)
            rect = icon.get_rect(topleft=(x, (height - icon_size[1]) // 2))
            self.verb_icons.append((verb, icon, rect))
            x += icon_size[0] + padding

        # Inventory button
        self.inventory_icon = create_verb_icon("use", (28, 28))
        # Tint it purple for inventory
        inv_overlay = pygame.Surface((28, 28), pygame.SRCALPHA)
        inv_overlay.fill((160, 100, 200, 100))
        self.inventory_icon.blit(inv_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.inventory_rect = self.inventory_icon.get_rect(
            topleft=(width - 70, (height - 28) // 2)
        )

        # Options button
        self.options_icon = create_verb_icon("look", (28, 28))
        opt_overlay = pygame.Surface((28, 28), pygame.SRCALPHA)
        opt_overlay.fill((100, 160, 200, 100))
        self.options_icon.blit(opt_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.options_rect = self.options_icon.get_rect(
            topleft=(width - 35, (height - 28) // 2)
        )

        # Health display
        self.health_display = HealthDisplay(width // 2 - 24, (height - 14) // 2)

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update which verb is being hovered."""
        self.hovered_verb = None
        for verb, _, rect in self.verb_icons:
            if rect.collidepoint(mouse_pos):
                self.hovered_verb = verb
                break

    def draw(self, surface: pygame.Surface, hero_health: int = 3) -> None:
        """Draw the verb bar."""
        # Gradient background
        gradient = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for y in range(self.rect.height):
            ratio = y / max(1, self.rect.height - 1)
            color = (
                int(40 + 80 * (1 - ratio)),
                int(15 + 35 * ratio),
                int(60 + 80 * ratio),
                240
            )
            pygame.draw.line(gradient, color, (0, y), (self.rect.width, y))
        surface.blit(gradient, self.rect)

        # Border with glow
        pygame.draw.rect(surface, COLORS.UI_BORDER, self.rect, 2)

        # Verb icons
        for verb, icon_surface, icon_rect in self.verb_icons:
            # Draw icon
            surface.blit(icon_surface, icon_rect)

            # Selection highlight
            if verb == self.selected_verb:
                pygame.draw.rect(surface, COLORS.NEON_GOLD, icon_rect.inflate(4, 4), 2)

            # Hover effect
            if verb == self.hovered_verb and verb != self.selected_verb:
                hover_overlay = pygame.Surface(icon_rect.size, pygame.SRCALPHA)
                hover_overlay.fill((255, 255, 255, 50))
                surface.blit(hover_overlay, icon_rect)

            # Keyboard shortcut hint
            key_num = list(VERB_KEYS.keys())[list(VERB_KEYS.values()).index(verb)]
            key_text = self.font.render(str(key_num - pygame.K_0), True, (200, 200, 220))
            surface.blit(key_text, (icon_rect.right - 8, icon_rect.bottom - 10))

        # Inventory and options
        surface.blit(self.inventory_icon, self.inventory_rect)
        surface.blit(self.options_icon, self.options_rect)

        # Labels
        inv_label = self.font.render("I", True, (200, 200, 220))
        opt_label = self.font.render("P", True, (200, 200, 220))
        surface.blit(inv_label, (self.inventory_rect.right - 8, self.inventory_rect.bottom - 10))
        surface.blit(opt_label, (self.options_rect.right - 8, self.options_rect.bottom - 10))

        # Health display
        self.health_display.draw(surface, hero_health)

    def handle_click(self, position: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click on verb bar."""
        for verb, _, rect in self.verb_icons:
            if rect.collidepoint(position):
                self.selected_verb = verb
                return "verb"
        if self.inventory_rect.collidepoint(position):
            return "inventory"
        if self.options_rect.collidepoint(position):
            return "options"
        return None

    def handle_key(self, key: int) -> Optional[str]:
        """Handle keyboard input. Returns action or None."""
        if key in VERB_KEYS:
            self.selected_verb = VERB_KEYS[key]
            return "verb"
        if key == pygame.K_i:
            return "inventory"
        if key == pygame.K_p:
            return "options"
        return None

    def cycle_next(self) -> Verb:
        """Cycle to the next verb."""
        verbs = [icon[0] for icon in self.verb_icons]
        index = verbs.index(self.selected_verb)
        self.selected_verb = verbs[(index + 1) % len(verbs)]
        return self.selected_verb

    def cycle_prev(self) -> Verb:
        """Cycle to the previous verb."""
        verbs = [icon[0] for icon in self.verb_icons]
        index = verbs.index(self.selected_verb)
        self.selected_verb = verbs[(index - 1) % len(verbs)]
        return self.selected_verb


class InventoryWindow:
    """Popup window for inventory management."""

    def __init__(self, inventory: Inventory, rect: pygame.Rect) -> None:
        self.inventory = inventory
        self.rect = rect
        self.visible = False
        self.font = load_serif_font(11)
        self.title_font = load_serif_font(14)
        self.item_rects: List[Tuple[Item, pygame.Rect]] = []
        self.hovered_item: Optional[Item] = None
        self.selected_index: int = 0

    def toggle(self) -> None:
        """Toggle inventory visibility."""
        self.visible = not self.visible
        if not self.visible:
            self.inventory.select_item(None)
        else:
            self.selected_index = 0

    def close(self) -> None:
        """Close the inventory window."""
        self.visible = False

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update which item is being hovered."""
        self.hovered_item = None
        for item, rect in self.item_rects:
            if rect.collidepoint(mouse_pos):
                self.hovered_item = item
                break

    def handle_key(self, key: int) -> Optional[Item]:
        """Handle keyboard navigation in inventory."""
        if not self.visible or not self.inventory.items:
            return None

        if key == pygame.K_LEFT:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == pygame.K_RIGHT:
            self.selected_index = min(len(self.inventory.items) - 1, self.selected_index + 1)
        elif key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 4)
        elif key == pygame.K_DOWN:
            self.selected_index = min(len(self.inventory.items) - 1, self.selected_index + 4)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if 0 <= self.selected_index < len(self.inventory.items):
                item = self.inventory.items[self.selected_index]
                if self.inventory.selected_item == item:
                    self.inventory.select_item(None)
                else:
                    self.inventory.select_item(item)
                return item
        elif key == pygame.K_ESCAPE or key == pygame.K_i:
            self.close()

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the inventory window."""
        if not self.visible:
            return

        # Background
        window = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(window, (*COLORS.UI_DARK, 245), window.get_rect(), border_radius=8)
        pygame.draw.rect(window, COLORS.UI_BORDER, window.get_rect(), 2, border_radius=8)

        # Title
        title = self.title_font.render("INVENTORY", True, COLORS.HOT_MAGENTA)
        window.blit(title, (self.rect.width // 2 - title.get_width() // 2, 8))

        # Item grid
        padding = 10
        columns = 4
        icon_size = 36
        spacing = 8
        start_y = 30

        self.item_rects = []

        for index, item in enumerate(self.inventory.items):
            row = index // columns
            column = index % columns
            x = padding + column * (icon_size + spacing)
            y = start_y + row * (icon_size + spacing + 14)

            icon_rect = pygame.Rect(x, y, icon_size, icon_size)

            # Draw item icon
            if item.icon:
                scaled_icon = pygame.transform.scale(item.icon, (icon_size, icon_size))
                window.blit(scaled_icon, icon_rect)
            else:
                pygame.draw.rect(window, item.icon_color, icon_rect)

            # Item border
            pygame.draw.rect(window, (60, 60, 80), icon_rect, 1)

            # Selection highlight (keyboard)
            if index == self.selected_index:
                pygame.draw.rect(window, COLORS.CYAN_GLOW, icon_rect.inflate(4, 4), 2)

            # Selected item highlight
            if self.inventory.selected_item and self.inventory.selected_item.name == item.name:
                pygame.draw.rect(window, COLORS.NEON_GOLD, icon_rect.inflate(6, 6), 2)

            # Hover highlight
            if self.hovered_item and self.hovered_item.name == item.name:
                hover = pygame.Surface(icon_rect.size, pygame.SRCALPHA)
                hover.fill((255, 255, 255, 40))
                window.blit(hover, icon_rect)

            # Item name
            name_surface = self.font.render(item.name, True, COLORS.UI_TEXT)
            name_x = x + icon_size // 2 - name_surface.get_width() // 2
            window.blit(name_surface, (max(2, name_x), y + icon_size + 2))

            self.item_rects.append((item, pygame.Rect(
                self.rect.x + x, self.rect.y + y, icon_size, icon_size
            )))

        # Item description for selected/hovered
        display_item = self.hovered_item or (
            self.inventory.items[self.selected_index]
            if self.inventory.items and self.selected_index < len(self.inventory.items)
            else None
        )

        if display_item:
            desc_text = display_item.description[:50] + "..." if len(display_item.description) > 50 else display_item.description
            desc = self.font.render(desc_text, True, (180, 180, 200))
            window.blit(desc, (padding, self.rect.height - 25))

        # Keyboard hints
        hints = self.font.render("Arrows: Navigate | Enter: Select | I/Esc: Close", True, (120, 120, 140))
        window.blit(hints, (self.rect.width // 2 - hints.get_width() // 2, self.rect.height - 12))

        surface.blit(window, self.rect)

    def handle_event(self, event: pygame.event.Event) -> Optional[Item]:
        """Handle events for inventory window."""
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


class PauseMenu:
    """Pause menu overlay."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.selected_option = 0

        self.title_font = load_serif_font(24)
        self.option_font = load_serif_font(16)

        self.options = ["Resume", "Save Game", "Load Game", "Quit"]

    def toggle(self) -> None:
        """Toggle pause menu."""
        self.visible = not self.visible
        self.selected_option = 0

    def handle_key(self, key: int) -> Optional[str]:
        """Handle keyboard input. Returns selected option or None."""
        if not self.visible:
            return None

        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.options[self.selected_option].lower().replace(" ", "_")
        elif key == pygame.K_ESCAPE or key == pygame.K_p:
            self.visible = False

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the pause menu."""
        if not self.visible:
            return

        # Dim overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Menu box
        box_width = 200
        box_height = 180
        box_x = (self.screen_width - box_width) // 2
        box_y = (self.screen_height - box_height) // 2

        pygame.draw.rect(surface, COLORS.UI_DARK, (box_x, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(surface, COLORS.UI_BORDER, (box_x, box_y, box_width, box_height), 2, border_radius=8)

        # Title
        title = self.title_font.render("PAUSED", True, COLORS.HOT_MAGENTA)
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, box_y + 15))

        # Options
        for i, option in enumerate(self.options):
            color = COLORS.NEON_GOLD if i == self.selected_option else COLORS.UI_TEXT
            text = self.option_font.render(option, True, color)
            y = box_y + 55 + i * 30
            surface.blit(text, (self.screen_width // 2 - text.get_width() // 2, y))

            if i == self.selected_option:
                # Selection indicator
                pygame.draw.polygon(surface, COLORS.NEON_GOLD, [
                    (box_x + 20, y + 8),
                    (box_x + 30, y + 3),
                    (box_x + 30, y + 13),
                ])
