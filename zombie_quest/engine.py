from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from .characters import Hero
from .data_loader import build_items, build_rooms, load_game_data
from .rooms import Hotspot, Room
from .ui import Inventory, InventoryWindow, MessageBox, Verb, VerbBar

ROOM_WIDTH = 320
ROOM_HEIGHT = 200
UI_BAR_HEIGHT = 40
MESSAGE_HEIGHT = 36
WINDOW_SIZE = (ROOM_WIDTH, ROOM_HEIGHT + UI_BAR_HEIGHT + MESSAGE_HEIGHT)


class GameEngine:
    def __init__(self, base_path: str) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Neon Dead Quest: Minneapolis '82")
        self.clock = pygame.time.Clock()

        data = load_game_data(base_path)
        self.rooms = build_rooms(data.get("rooms", []))
        hero_data = data.get("hero", {})
        start_room_id = hero_data.get("start_room") or next(iter(self.rooms.keys()))
        self.current_room: Room = self.rooms[start_room_id]
        hero_start = tuple(hero_data.get("position", (ROOM_WIDTH // 2, int(ROOM_HEIGHT * 0.8))))
        self.hero = Hero(hero_start)

        self.room_surface = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)

        self.verb_bar = VerbBar(WINDOW_SIZE[0], UI_BAR_HEIGHT)
        self.message_box = MessageBox(WINDOW_SIZE[0], MESSAGE_HEIGHT)
        self.message_box.rect.topleft = (0, WINDOW_SIZE[1] - MESSAGE_HEIGHT)

        self.inventory = Inventory()
        self.inventory_window = InventoryWindow(
            self.inventory,
            pygame.Rect(40, UI_BAR_HEIGHT + 20, WINDOW_SIZE[0] - 80, 140),
        )

        self.items_catalog = build_items(data.get("items", []))
        for item_name in data.get("starting_inventory", []):
            item = self.items_catalog.get(item_name)
            if item:
                self.inventory.add_item(item)

        self.pending_interaction: Optional[Tuple[Hotspot, Verb]] = None
        self.running = True
        initial_message = self.current_room.entry_message or "The Minneapolis night hums with feedback."
        if initial_message:
            self.message_box.show(initial_message)

    def run(self) -> None:  # pragma: no cover - interactive loop
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.inventory_window.visible:
                        selected = self.inventory_window.handle_event(event)
                        if selected:
                            self.message_box.show(f"Selected {selected.name}.")
                        continue
                    if self.verb_bar.rect.collidepoint(event.pos):
                        action = self.verb_bar.handle_click(event.pos)
                        if action == "inventory":
                            self.inventory_window.toggle()
                        elif action == "options":
                            self.message_box.show("The options screen flickers briefly, then vanishes.")
                        continue
                    if self.inventory_window.visible and self.inventory_window.rect.collidepoint(event.pos):
                        continue
                    self.handle_room_click(event.pos)
                elif event.button == 3:
                    verb = self.verb_bar.cycle_next()
                    self.message_box.show(f"Selected {verb.value.title()} icon.")
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.inventory_window.visible:
                    self.inventory_window.handle_event(event)

    def handle_room_click(self, position: Tuple[int, int]) -> None:
        room_pos = self.screen_to_room(position)
        if room_pos is None:
            return
        verb = self.verb_bar.selected_verb
        if verb == Verb.WALK:
            self.hero.set_destination(room_pos, self.current_room.pathfinder)
            self.message_box.show("You weave through the neon throng.")
            self.pending_interaction = None
            return
        hotspot = self.current_room.find_hotspot((int(room_pos[0]), int(room_pos[1])))
        if not hotspot:
            self.message_box.show("There's nothing of interest there.")
            return
        self.request_hotspot_interaction(hotspot, verb)

    def request_hotspot_interaction(self, hotspot: Hotspot, verb: Verb) -> None:
        target = hotspot.walk_position or (hotspot.rect.centerx, hotspot.rect.bottom)
        self.hero.set_destination(target, self.current_room.pathfinder)
        self.pending_interaction = (hotspot, verb)

    def screen_to_room(self, position: Tuple[int, int]) -> Optional[Tuple[float, float]]:
        x, y = position
        if y < UI_BAR_HEIGHT or y >= UI_BAR_HEIGHT + ROOM_HEIGHT:
            return None
        room_y = y - UI_BAR_HEIGHT
        return float(x), float(room_y)

    def update(self, dt: float) -> None:
        self.hero.update(dt)
        self.current_room.update(dt, self.hero)
        if self.pending_interaction and self.hero.has_arrived():
            hotspot, verb = self.pending_interaction
            self.pending_interaction = None
            self.perform_hotspot_action(hotspot, verb)
        self.message_box.update(dt)

    def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
        selected_item = self.inventory.selected_item
        interaction_outcome = "default"
        if verb == Verb.LOOK:
            message = hotspot.message_for("look", interaction_outcome)
        elif verb == Verb.TALK:
            message = hotspot.message_for("talk", interaction_outcome)
        elif verb == Verb.USE:
            if hotspot.required_item:
                if selected_item and selected_item.name == hotspot.required_item:
                    interaction_outcome = "success"
                    message = hotspot.message_for("use", interaction_outcome)
                    if hotspot.remove_item and verb.value in hotspot.remove_item_triggers:
                        self.inventory.remove_item(hotspot.remove_item)
                    if hotspot.give_item and verb.value in hotspot.give_item_triggers:
                        self.give_item_to_inventory(hotspot.give_item)
                        hotspot.give_item = None
                    if selected_item:
                        self.inventory.select_item(None)
                else:
                    interaction_outcome = "missing"
                    message = hotspot.message_for("use", interaction_outcome)
            else:
                interaction_outcome = "success"
                message = hotspot.message_for("use", interaction_outcome)
                if hotspot.give_item and verb.value in hotspot.give_item_triggers:
                    self.give_item_to_inventory(hotspot.give_item)
                    hotspot.give_item = None
        else:
            message = hotspot.message_for(verb.value, interaction_outcome)
        if hotspot.give_item and verb.value in hotspot.give_item_triggers and interaction_outcome != "missing":
            self.give_item_to_inventory(hotspot.give_item)
            hotspot.give_item = None
        if hotspot.remove_item and verb.value in hotspot.remove_item_triggers and interaction_outcome == "success":
            self.inventory.remove_item(hotspot.remove_item)
        should_transition = False
        if hotspot.target_room and hotspot.transition_verb == verb.value:
            if hotspot.requires_success_for_transition:
                should_transition = interaction_outcome == "success"
            else:
                should_transition = interaction_outcome != "missing"
        transition_performed = False
        if should_transition:
            combined_message_parts: List[str] = []
            if message:
                combined_message_parts.append(message)
            transition_text = hotspot.transition_message
            if transition_text:
                combined_message_parts.append(transition_text)
            self.change_room(
                hotspot.target_room,
                hotspot.target_position,
                message=None,
                announce=False,
            )
            if not combined_message_parts:
                combined_message = self.current_room.entry_message or f"You arrive at {self.current_room.name}."
            else:
                combined_message = " ".join(combined_message_parts)
            if combined_message:
                self.message_box.show(combined_message)
            transition_performed = True
        if transition_performed:
            return
        if not message:
            message = "Nothing happens."
        self.message_box.show(message)

    def give_item_to_inventory(self, item_name: str) -> None:
        item = self.items_catalog.get(item_name)
        if item and not self.inventory.has_item(item.name):
            self.inventory.add_item(item)
            self.message_box.show(f"You stash the {item.name} in your flight case.")

    def change_room(
        self,
        room_id: str,
        position: Optional[Tuple[int, int]] = None,
        message: Optional[str] = None,
        announce: bool = True,
    ) -> None:
        room = self.rooms.get(room_id)
        if not room:
            return
        self.current_room = room
        destination = position or room.default_entry
        self.hero.position.update(destination)
        self.hero.path = []
        self.hero.current_target = None
        self.pending_interaction = None
        if announce:
            entry_message = message or room.entry_message or f"You arrive at {room.name}."
            if entry_message:
                self.message_box.show(entry_message)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        self.current_room.draw(self.room_surface, self.hero)
        self.screen.blit(self.room_surface, (0, UI_BAR_HEIGHT))
        self.verb_bar.draw(self.screen)
        self.message_box.draw(self.screen)
        if self.inventory_window.visible:
            self.inventory_window.draw(self.screen)
