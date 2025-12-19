"""Enhanced inventory system with tooltips, drag-and-drop, and visual feedback.

Features:
- Rich tooltips on hover with item stats
- Drag-and-drop to use items
- Visual feedback when inventory is full
- Smooth animations for item add/remove
- Item stacking and sorting
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from .config import COLORS, ANIMATION
from .ui import Item, Inventory
from .resources import load_serif_font

Color = Tuple[int, int, int]


@dataclass
class ItemSlot:
    """A visual slot in the inventory grid."""
    rect: pygame.Rect
    item: Optional[Item] = None
    index: int = 0
    hover_time: float = 0.0
    pulse_time: float = 0.0


class ItemTooltip:
    """Rich tooltip display for inventory items."""

    def __init__(self) -> None:
        self.font_title = load_serif_font(12)
        self.font_body = load_serif_font(10)
        self.padding = 8
        self.show_delay = 0.4  # Seconds before tooltip shows
        self.current_time = 0.0
        self.visible = False

    def start_hover(self) -> None:
        """Start hovering over an item."""
        self.current_time = 0.0
        self.visible = False

    def update(self, dt: float, is_hovering: bool) -> None:
        """Update tooltip visibility."""
        if is_hovering:
            self.current_time += dt
            if self.current_time >= self.show_delay:
                self.visible = True
        else:
            self.current_time = 0.0
            self.visible = False

    def draw(self, surface: pygame.Surface, item: Item, position: Tuple[int, int]) -> None:
        """Draw tooltip for an item."""
        if not self.visible:
            return

        # Prepare text
        title = self.font_title.render(item.name, True, COLORS.NEON_GOLD)
        desc_lines = self._wrap_text(item.description, 200, self.font_body)

        # Calculate tooltip size
        width = max(title.get_width(), max((line.get_width() for line in desc_lines), default=0)) + self.padding * 2
        height = title.get_height() + sum(line.get_height() for line in desc_lines) + self.padding * 3

        # Position tooltip (avoid screen edges)
        x = position[0] + 15
        y = position[1] + 15

        # Keep on screen
        screen_width, screen_height = surface.get_size()
        if x + width > screen_width:
            x = position[0] - width - 15
        if y + height > screen_height:
            y = position[1] - height - 15

        tooltip_rect = pygame.Rect(x, y, width, height)

        # Draw background with glow
        self._draw_background(surface, tooltip_rect)

        # Draw title
        y_offset = y + self.padding
        surface.blit(title, (x + self.padding, y_offset))
        y_offset += title.get_height() + self.padding // 2

        # Draw separator line
        pygame.draw.line(
            surface,
            COLORS.UI_BORDER,
            (x + self.padding, y_offset),
            (x + width - self.padding, y_offset),
            1
        )
        y_offset += self.padding // 2

        # Draw description
        for line in desc_lines:
            surface.blit(line, (x + self.padding, y_offset))
            y_offset += line.get_height()

    def _draw_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw tooltip background with glow effect."""
        # Outer glow
        for i in range(3):
            glow_rect = rect.inflate(i * 4, i * 4)
            alpha = 40 - i * 10
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf,
                (*COLORS.HOT_MAGENTA, alpha),
                glow_rect,
                border_radius=4
            )
            surface.blit(glow_surf, (0, 0))

        # Main background
        pygame.draw.rect(surface, COLORS.UI_DARK, rect, border_radius=4)
        pygame.draw.rect(surface, COLORS.UI_BORDER, rect, 2, border_radius=4)

    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[pygame.Surface]:
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_surface = font.render(' '.join(current_line), True, COLORS.UI_TEXT)

            if test_surface.get_width() > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(font.render(' '.join(current_line), True, COLORS.UI_TEXT))
                    current_line = [word]
                else:
                    lines.append(test_surface)
                    current_line = []

        if current_line:
            lines.append(font.render(' '.join(current_line), True, COLORS.UI_TEXT))

        return lines


class DragDropController:
    """Handles drag-and-drop for inventory items."""

    def __init__(self) -> None:
        self.dragging = False
        self.dragged_item: Optional[Item] = None
        self.drag_start_pos: Tuple[int, int] = (0, 0)
        self.drag_current_pos: Tuple[int, int] = (0, 0)
        self.drag_offset: Tuple[int, int] = (0, 0)
        self.source_slot_index: int = -1

    def start_drag(self, item: Item, mouse_pos: Tuple[int, int],
                  item_rect: pygame.Rect, slot_index: int) -> None:
        """Start dragging an item."""
        self.dragging = True
        self.dragged_item = item
        self.drag_start_pos = mouse_pos
        self.drag_current_pos = mouse_pos
        self.drag_offset = (
            item_rect.centerx - mouse_pos[0],
            item_rect.centery - mouse_pos[1]
        )
        self.source_slot_index = slot_index

    def update_drag(self, mouse_pos: Tuple[int, int]) -> None:
        """Update drag position."""
        if self.dragging:
            self.drag_current_pos = mouse_pos

    def end_drag(self) -> Optional[Tuple[Item, int]]:
        """End drag and return (item, source_slot_index) if was dragging."""
        if self.dragging:
            result = (self.dragged_item, self.source_slot_index)
            self.dragging = False
            self.dragged_item = None
            return result
        return None

    def cancel_drag(self) -> None:
        """Cancel current drag."""
        self.dragging = False
        self.dragged_item = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw dragged item following cursor."""
        if not self.dragging or not self.dragged_item:
            return

        # Draw item icon at cursor with slight transparency
        if self.dragged_item.icon:
            icon = self.dragged_item.icon.copy()
            icon.set_alpha(200)

            # Position with offset
            draw_x = self.drag_current_pos[0] + self.drag_offset[0] - icon.get_width() // 2
            draw_y = self.drag_current_pos[1] + self.drag_offset[1] - icon.get_height() // 2

            # Draw shadow
            shadow = pygame.Surface((icon.get_width() + 4, icon.get_height() + 4), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            surface.blit(shadow, (draw_x - 2, draw_y + 2))

            # Draw icon
            surface.blit(icon, (draw_x, draw_y))


class EnhancedInventoryWindow:
    """Enhanced inventory window with all UX improvements."""

    def __init__(self, inventory: Inventory, rect: pygame.Rect) -> None:
        self.inventory = inventory
        self.rect = rect
        self.visible = False

        # UI components
        self.tooltip = ItemTooltip()
        self.drag_drop = DragDropController()

        # Fonts
        self.font = load_serif_font(11)
        self.title_font = load_serif_font(14)

        # Slots
        self.slots: List[ItemSlot] = []
        self.hovered_slot: Optional[ItemSlot] = None
        self.selected_index: int = 0

        # Full inventory feedback
        self.full_message_alpha = 0.0
        self.full_message_timer = 0.0

        # Animation
        self.time = 0.0

    def toggle(self) -> None:
        """Toggle inventory visibility."""
        self.visible = not self.visible
        if not self.visible:
            self.inventory.select_item(None)
            self.drag_drop.cancel_drag()
        else:
            self.selected_index = 0
            self._rebuild_slots()

    def close(self) -> None:
        """Close the inventory window."""
        self.visible = False
        self.drag_drop.cancel_drag()

    def show_full_message(self) -> None:
        """Show 'inventory full' feedback."""
        self.full_message_alpha = 255.0
        self.full_message_timer = 2.0

    def _rebuild_slots(self) -> None:
        """Rebuild slot grid from current inventory."""
        self.slots = []

        columns = 4
        icon_size = 36
        spacing = 8
        padding = 10
        start_y = 30

        for index in range(self.inventory.max_items):
            row = index // columns
            column = index % columns
            x = self.rect.x + padding + column * (icon_size + spacing)
            y = self.rect.y + start_y + row * (icon_size + spacing + 14)

            slot = ItemSlot(
                rect=pygame.Rect(x, y, icon_size, icon_size),
                item=self.inventory.items[index] if index < len(self.inventory.items) else None,
                index=index
            )
            self.slots.append(slot)

    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        """Update inventory animations and states."""
        if not self.visible:
            return

        self.time += dt

        # Rebuild slots if needed
        if len(self.slots) != self.inventory.max_items:
            self._rebuild_slots()

        # Update slots
        self.hovered_slot = None
        for slot in self.slots:
            # Update item reference
            if slot.index < len(self.inventory.items):
                slot.item = self.inventory.items[slot.index]
            else:
                slot.item = None

            # Check hover
            if slot.rect.collidepoint(mouse_pos):
                self.hovered_slot = slot
                slot.hover_time += dt
            else:
                slot.hover_time = 0.0

            # Update pulse animation
            slot.pulse_time += dt

        # Update tooltip
        if self.hovered_slot and self.hovered_slot.item:
            self.tooltip.update(dt, True)
        else:
            self.tooltip.update(dt, False)

        # Update drag
        self.drag_drop.update_drag(mouse_pos)

        # Update full message
        if self.full_message_timer > 0:
            self.full_message_timer -= dt
            if self.full_message_timer <= 0:
                self.full_message_alpha = 0.0
        if self.full_message_alpha > 0:
            self.full_message_alpha = max(0, self.full_message_alpha - 300 * dt)

    def handle_mouse_down(self, event: pygame.event.Event) -> Optional[Item]:
        """Handle mouse button down."""
        if not self.visible:
            return None

        if event.button == 1:  # Left click
            # Check if clicking outside window
            if not self.rect.collidepoint(event.pos):
                self.toggle()
                return None

            # Check slots
            if self.hovered_slot and self.hovered_slot.item:
                # Start drag
                self.drag_drop.start_drag(
                    self.hovered_slot.item,
                    event.pos,
                    self.hovered_slot.rect,
                    self.hovered_slot.index
                )
                return self.hovered_slot.item

        return None

    def handle_mouse_up(self, event: pygame.event.Event) -> Optional[Tuple[str, Item]]:
        """Handle mouse button up. Returns action and item if applicable."""
        if not self.visible or event.button != 1:
            return None

        # End drag
        drag_result = self.drag_drop.end_drag()
        if drag_result:
            item, source_index = drag_result

            # Check if dropped on hotspot or game world (implement in game engine)
            if not self.rect.collidepoint(event.pos):
                # Dropped outside inventory - use item
                return ("use", item)

            # Dropped on another slot - reorder (optional feature)
            # For now, just select the item
            if self.inventory.selected_item == item:
                self.inventory.select_item(None)
            else:
                self.inventory.select_item(item)
            return ("select", item)

        # Regular click
        if self.hovered_slot and self.hovered_slot.item:
            item = self.hovered_slot.item
            if self.inventory.selected_item == item:
                self.inventory.select_item(None)
            else:
                self.inventory.select_item(item)
            return ("select", item)

        return None

    def handle_key(self, key: int) -> Optional[Item]:
        """Handle keyboard navigation."""
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

    def draw(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]) -> None:
        """Draw the enhanced inventory window."""
        if not self.visible:
            return

        # Background
        window = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(window, (*COLORS.UI_DARK, 245), window.get_rect(), border_radius=8)
        pygame.draw.rect(window, COLORS.UI_BORDER, window.get_rect(), 2, border_radius=8)

        # Title
        title = self.title_font.render("INVENTORY", True, COLORS.HOT_MAGENTA)
        window.blit(title, (self.rect.width // 2 - title.get_width() // 2, 8))

        # Full message if showing
        if self.full_message_alpha > 0:
            self._draw_full_message(window)

        # Capacity counter
        capacity_text = f"{len(self.inventory.items)}/{self.inventory.max_items}"
        capacity_color = COLORS.NEON_GOLD if len(self.inventory.items) < self.inventory.max_items else (255, 100, 100)
        capacity = self.font.render(capacity_text, True, capacity_color)
        window.blit(capacity, (self.rect.width - capacity.get_width() - 10, 10))

        surface.blit(window, self.rect)

        # Draw slots on main surface (for proper positioning)
        for slot in self.slots:
            self._draw_slot(surface, slot)

        # Draw tooltip
        if self.hovered_slot and self.hovered_slot.item and not self.drag_drop.dragging:
            self.tooltip.draw(surface, self.hovered_slot.item, mouse_pos)

        # Draw dragged item
        self.drag_drop.draw(surface)

        # Keyboard hints
        hints_surface = pygame.Surface((self.rect.width, 20), pygame.SRCALPHA)
        hints = self.font.render("Arrows: Navigate | Enter: Select | Drag: Use | I/Esc: Close", True, (120, 120, 140))
        hints_surface.blit(hints, (self.rect.width // 2 - hints.get_width() // 2, 0))
        surface.blit(hints_surface, (self.rect.x, self.rect.y + self.rect.height - 20))

    def _draw_slot(self, surface: pygame.Surface, slot: ItemSlot) -> None:
        """Draw a single inventory slot."""
        # Empty slot background
        slot_color = (40, 35, 50) if slot.item else (30, 25, 40)
        pygame.draw.rect(surface, slot_color, slot.rect, border_radius=4)
        pygame.draw.rect(surface, (60, 60, 80), slot.rect, 1, border_radius=4)

        # Don't draw item if being dragged
        if slot.item and not (self.drag_drop.dragging and self.drag_drop.source_slot_index == slot.index):
            # Draw item icon
            if slot.item.icon:
                icon = pygame.transform.scale(slot.item.icon, (slot.rect.width - 4, slot.rect.height - 4))
                surface.blit(icon, (slot.rect.x + 2, slot.rect.y + 2))
            else:
                pygame.draw.rect(surface, slot.item.icon_color, slot.rect.inflate(-4, -4))

            # Selected highlight
            if self.inventory.selected_item and self.inventory.selected_item.name == slot.item.name:
                pygame.draw.rect(surface, COLORS.NEON_GOLD, slot.rect.inflate(6, 6), 2, border_radius=4)

            # Keyboard selection highlight
            if slot.index == self.selected_index:
                pygame.draw.rect(surface, COLORS.CYAN_GLOW, slot.rect.inflate(4, 4), 2, border_radius=4)

            # Hover effect
            if slot == self.hovered_slot and not self.drag_drop.dragging:
                hover_surf = pygame.Surface(slot.rect.size, pygame.SRCALPHA)
                hover_surf.fill((255, 255, 255, 40))
                surface.blit(hover_surf, slot.rect)

                # Pulsing glow
                pulse = (math.sin(self.time * 4) + 1) / 2
                glow_alpha = int(50 + pulse * 30)
                pygame.draw.rect(surface, (*COLORS.NEON_GOLD, glow_alpha), slot.rect.inflate(4, 4), 2, border_radius=4)

    def _draw_full_message(self, surface: pygame.Surface) -> None:
        """Draw 'inventory full' warning."""
        message = "INVENTORY FULL!"
        msg_surface = self.title_font.render(message, True, (255, 100, 100))

        # Position in center
        msg_x = self.rect.width // 2 - msg_surface.get_width() // 2
        msg_y = 40

        # Pulsing background
        bg_rect = msg_surface.get_rect(topleft=(msg_x - 8, msg_y - 4)).inflate(16, 8)
        bg_alpha = int(self.full_message_alpha * 0.8)
        pygame.draw.rect(surface, (*COLORS.UI_DARK, bg_alpha), bg_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 100, 100, int(self.full_message_alpha)), bg_rect, 2, border_radius=4)

        # Message
        msg_surface.set_alpha(int(self.full_message_alpha))
        surface.blit(msg_surface, (msg_x, msg_y))
