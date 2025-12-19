"""Tests for UI system."""
import pytest
import pygame

# Initialize pygame for testing
pygame.init()


from zombie_quest.ui import (
    Verb,
    Item,
    Inventory,
    MessageBox,
    VerbBar,
    HealthDisplay,
    PauseMenu,
    VERB_KEYS,
)


class TestVerb:
    """Test verb enumeration."""

    def test_verb_values(self):
        assert Verb.WALK.value == "walk"
        assert Verb.LOOK.value == "look"
        assert Verb.USE.value == "use"
        assert Verb.TALK.value == "talk"


class TestItem:
    """Test inventory item."""

    def test_item_creation(self):
        item = Item(
            name="Test Item",
            description="A test item",
            icon_color=(255, 0, 0)
        )
        assert item.name == "Test Item"
        assert item.description == "A test item"
        assert item.icon is not None  # Auto-generated


class TestInventory:
    """Test inventory management."""

    def test_inventory_creation(self):
        inv = Inventory()
        assert len(inv.items) == 0

    def test_add_item(self):
        inv = Inventory()
        item = Item("Key", "A rusty key", (200, 180, 100))
        result = inv.add_item(item)
        assert result is True
        assert len(inv.items) == 1

    def test_inventory_limit(self):
        inv = Inventory(max_items=2)
        inv.add_item(Item("Item1", "Desc", (100, 100, 100)))
        inv.add_item(Item("Item2", "Desc", (100, 100, 100)))
        result = inv.add_item(Item("Item3", "Desc", (100, 100, 100)))
        assert result is False
        assert len(inv.items) == 2

    def test_remove_item(self):
        inv = Inventory()
        item = Item("Key", "A key", (200, 180, 100))
        inv.add_item(item)
        removed = inv.remove_item("Key")
        assert removed is not None
        assert removed.name == "Key"
        assert len(inv.items) == 0

    def test_has_item(self):
        inv = Inventory()
        inv.add_item(Item("Key", "A key", (200, 180, 100)))
        assert inv.has_item("Key") is True
        assert inv.has_item("Lock") is False

    def test_select_item(self):
        inv = Inventory()
        item = Item("Key", "A key", (200, 180, 100))
        inv.add_item(item)
        inv.select_item(item)
        assert inv.selected_item == item


class TestMessageBox:
    """Test message box functionality."""

    def test_message_box_creation(self):
        msg = MessageBox(320, 36)
        assert msg.full_message == ""
        assert msg.is_typing is False

    def test_show_message(self):
        msg = MessageBox(320, 36)
        msg.show("Hello world!")
        assert msg.full_message == "Hello world!"
        assert msg.is_typing is True

    def test_skip_typing(self):
        msg = MessageBox(320, 36)
        msg.show("Hello world!")
        msg.skip_typing()
        assert msg.displayed_message == "Hello world!"
        assert msg.is_typing is False


class TestVerbBar:
    """Test verb selection bar."""

    def test_verb_bar_creation(self):
        vb = VerbBar(320, 40)
        assert vb.selected_verb == Verb.WALK

    def test_cycle_next(self):
        vb = VerbBar(320, 40)
        vb.cycle_next()
        assert vb.selected_verb == Verb.LOOK

    def test_cycle_prev(self):
        vb = VerbBar(320, 40)
        vb.cycle_prev()
        assert vb.selected_verb == Verb.TALK

    def test_handle_key(self):
        vb = VerbBar(320, 40)
        result = vb.handle_key(pygame.K_2)  # Look
        assert result == "verb"
        assert vb.selected_verb == Verb.LOOK


class TestHealthDisplay:
    """Test health display."""

    def test_health_display_creation(self):
        hd = HealthDisplay(0, 0, max_health=3)
        assert hd.max_health == 3
        assert hd.heart_full is not None
        assert hd.heart_empty is not None


class TestPauseMenu:
    """Test pause menu functionality."""

    def test_pause_menu_creation(self):
        pm = PauseMenu(320, 276)
        assert pm.visible is False
        assert pm.selected_option == 0

    def test_toggle(self):
        pm = PauseMenu(320, 276)
        pm.toggle()
        assert pm.visible is True
        pm.toggle()
        assert pm.visible is False

    def test_navigation(self):
        pm = PauseMenu(320, 276)
        pm.visible = True
        pm.handle_key(pygame.K_DOWN)
        assert pm.selected_option == 1
        pm.handle_key(pygame.K_UP)
        assert pm.selected_option == 0


class TestVerbKeys:
    """Test verb keyboard shortcuts."""

    def test_verb_keys_mapping(self):
        assert VERB_KEYS[pygame.K_1] == Verb.WALK
        assert VERB_KEYS[pygame.K_2] == Verb.LOOK
        assert VERB_KEYS[pygame.K_3] == Verb.USE
        assert VERB_KEYS[pygame.K_4] == Verb.TALK
