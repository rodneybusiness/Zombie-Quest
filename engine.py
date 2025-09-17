"""Core game engine loop for the Sierra-inspired Zombie Quest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

from characters import Hero
from inventory import Inventory
from items import ItemDefinition
from rooms import Hotspot, Room
from settings import (
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_BAR_HEIGHT,
    VERBS,
    WORLD_HEIGHT,
    WORLD_SCALE,
    WORLD_WIDTH,
)
from ui import CursorManager, InventoryWindow, MessageBar, VerbBar


class GameEngine:
    def __init__(self, screen: pygame.Surface, data_path: Path) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.hero = Hero((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.inventory = Inventory()
        self.verb_bar = VerbBar()
        self.inventory_window = InventoryWindow()
        self.message_bar = MessageBar()
        self.cursor = CursorManager()
        self.current_verb_index = 0
        self.current_room: Room | None = None
        self.rooms: Dict[str, Room] = {}
        self.item_catalog: Dict[str, ItemDefinition] = {}
        self._load_data(data_path)
        self.room_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
        self.scaled_room_surface = pygame.Surface((WORLD_WIDTH * WORLD_SCALE, WORLD_HEIGHT * WORLD_SCALE))
        self.message_bar.show_message("The night is still. Click with Walk to explore the ruins.")

    def _load_data(self, data_path: Path) -> None:
        data = json.loads(Path(data_path).read_text(encoding="utf-8"))
        self.item_catalog = {
            item_data["name"]: ItemDefinition(
                name=item_data["name"],
                description=item_data.get("description", ""),
                icon_color=tuple(item_data.get("icon_color", [180, 180, 180])),
            )
            for item_data in data.get("items", [])
        }
        for room_data in data.get("rooms", []):
            room = Room(room_data, self.hero)
            self.rooms[room.id] = room
        start_room_id = data.get("start_room", data.get("rooms", [{}])[0].get("id"))
        self.current_room = self.rooms[start_room_id]
        if self.current_room:
            self.hero.set_position(self.current_room.start_position)

    @property
    def current_verb(self) -> str:
        return VERBS[self.current_verb_index]

    def cycle_verb(self, step: int = 1) -> None:
        self.current_verb_index = (self.current_verb_index + step) % len(VERBS)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    self.cycle_verb(1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._on_left_click(event.pos)
                elif event.button == 3:
                    self.cycle_verb(1)

    def _on_left_click(self, pos: Tuple[int, int]) -> None:
        if self.inventory_window.visible:
            selected = self.inventory_window.handle_click(pos, self.inventory)
            if selected:
                self.message_bar.show_message(f"{selected.name}: {selected.description}")
            else:
                # Click outside closes inventory
                if not self.inventory_window.rect.collidepoint(pos):
                    self.inventory_window.hide()
            return

        ui_response = self.verb_bar.handle_click(pos)
        if ui_response:
            if "verb" in ui_response:
                self._set_verb(ui_response["verb"])
            elif "inventory" in ui_response:
                self.inventory_window.toggle()
            elif "options" in ui_response:
                self.message_bar.show_message("Options are not available in this demo.")
            return

        if pos[1] >= UI_BAR_HEIGHT and pos[1] < UI_BAR_HEIGHT + WORLD_HEIGHT * WORLD_SCALE:
            world_x = pos[0] / WORLD_SCALE
            world_y = (pos[1] - UI_BAR_HEIGHT) / WORLD_SCALE
            self._handle_world_interaction((world_x, world_y))

    def _set_verb(self, verb: str) -> None:
        if verb in VERBS:
            self.current_verb_index = VERBS.index(verb)

    def _handle_world_interaction(self, world_pos: Tuple[float, float]) -> None:
        if not self.current_room:
            return
        verb = self.current_verb
        if verb == "WALK":
            self._walk_to(world_pos)
            return
        hotspot = self.current_room.find_hotspot((int(world_pos[0]), int(world_pos[1])))
        if not hotspot:
            self.message_bar.show_message("You don't see anything interesting there.")
            return
        self._interact_with_hotspot(hotspot, verb)

    def _walk_to(self, world_pos: Tuple[float, float]) -> None:
        if not self.current_room:
            return
        path = self.current_room.pathfinder.find_path(tuple(self.hero.position), world_pos)
        if not path:
            self.message_bar.show_message("You can't walk there.")
            return
        if path and (pygame.Vector2(path[0]) - self.hero.position).length() < 1.0:
            path = path[1:]
        self.hero.set_path(path)

    def _interact_with_hotspot(self, hotspot: Hotspot, verb: str) -> None:
        action = hotspot.action_for(verb)
        if not action:
            self.message_bar.show_message(f"Nothing happens when you {verb.lower()} the {hotspot.name.lower()}.")
            return

        message = action.text or "Nothing happens."
        selected_item = self.inventory.selected_item

        if action.gives_item and not hotspot.state.get("item_taken"):
            definition = self.item_catalog.get(action.gives_item)
            if definition and not self.inventory.has_item(definition.name):
                item = definition.create_instance()
                self.inventory.add_item(item)
                self.inventory.select_item(item)
                hotspot.state["item_taken"] = True
                message = action.success_text or f"You pick up the {item.name}."
            else:
                message = action.failure_text or message
        elif action.requires_item:
            if selected_item and selected_item.name == action.requires_item:
                message = action.success_text or message
                if action.consumes_item:
                    self.inventory.remove_item(selected_item.name)
                    self.inventory.clear_selection()
                if action.gives_item:
                    definition = self.item_catalog.get(action.gives_item)
                    if definition and not self.inventory.has_item(definition.name):
                        new_item = definition.create_instance()
                        self.inventory.add_item(new_item)
                        message = action.success_text or f"You receive {new_item.name}."
            else:
                if selected_item is None:
                    message = action.failure_text or "You need to select the proper item first."
                else:
                    message = action.failure_text or f"{selected_item.name} doesn't help here."
        elif verb == "USE" and selected_item:
            message = action.failure_text or f"Using {selected_item.name} here accomplishes nothing."
        elif verb == "TALK" and not message:
            message = "Only silence answers you."

        self.message_bar.show_message(message)

    def _update(self, dt: float) -> None:
        if self.current_room:
            self.current_room.update(dt)
        self.hero.update(dt)
        self.message_bar.update(dt)

    def _draw(self) -> None:
        self.screen.fill((0, 0, 0))
        if self.current_room:
            self.current_room.draw(self.room_surface)
            pygame.transform.smoothscale(self.room_surface, self.scaled_room_surface.get_size(), self.scaled_room_surface)
            self.screen.blit(self.scaled_room_surface, (0, UI_BAR_HEIGHT))
        self.verb_bar.draw(self.screen, self.current_verb, self.inventory.selected_item)
        self.inventory_window.draw(self.screen, self.inventory)
        self.message_bar.draw(self.screen)
        self.cursor.draw(self.screen, self.current_verb, self.inventory.selected_item)


def run_game(data_path: str) -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Quest - SCI Edition")
    engine = GameEngine(screen, Path(data_path))
    engine.run()
    pygame.quit()
