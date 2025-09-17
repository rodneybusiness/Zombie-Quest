"""Core game engine for the SCI-inspired Zombie Quest."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import pygame

import assets
from characters import Hero, Zombie
from rooms import Hotspot, Room
from ui import Inventory, InventoryWindow, Item, MessageWindow, Verb, VerbBar

Vector2 = Tuple[float, float]


def load_game_data(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf8") as handle:
        return json.load(handle)


@dataclass
class PendingAction:
    hotspot: Hotspot
    verb: Verb
    target_point: Vector2
    action_data: object


class Game:
    def __init__(self, data_path: str) -> None:
        self.width, self.height = assets.VGA_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Zombie Quest VGA")
        self.clock = pygame.time.Clock()
        self.running = True

        data = load_game_data(data_path)
        self.rooms: Dict[str, Room] = {
            room_id: Room(room_id, room_data) for room_id, room_data in data["rooms"].items()
        }
        self.current_room_id: str = data.get("start_room", next(iter(self.rooms)))
        self.inventory = Inventory()
        self.items_catalog: Dict[str, Item] = {
            item_id: Item(item_id, item_data["name"], item_data["description"], tuple(item_data["icon_color"]))
            for item_id, item_data in data.get("items", {}).items()
        }
        self.flags = set(data.get("starting_flags", []))
        current_room = self.rooms[self.current_room_id]
        self.hero = Hero(current_room.start_position)
        self.verb_bar = VerbBar(self.width, [Verb.WALK, Verb.LOOK, Verb.USE, Verb.TALK])
        self.inventory_window = InventoryWindow(260, 200)
        self.message_window = MessageWindow(self.width)
        self.selected_verb = Verb.WALK
        self.selected_item_id: Optional[str] = None
        self.pending_action: Optional[PendingAction] = None
        self.zombies: Dict[str, Tuple[Zombie, ...]] = self._create_zombies()
        self.zombie_warning_timer = 0.0
        pygame.mouse.set_visible(False)

    def _create_zombies(self) -> Dict[str, Tuple[Zombie, ...]]:
        result: Dict[str, Tuple[Zombie, ...]] = {}
        for room_id, room in self.rooms.items():
            zombies = []
            for zombie_data in room.zombie_data:
                position = tuple(zombie_data.get("position", (room.start_position[0], room.start_position[1] - 20)))
                patrol = zombie_data.get("patrol")
                zombies.append(Zombie(position, patrol_points=patrol))
            result[room_id] = tuple(zombies)
        return result

    @property
    def current_room(self) -> Room:
        return self.rooms[self.current_room_id]

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(30) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    self.cycle_verb()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_left_click(event.pos)
                elif event.button == 3:
                    self.cycle_verb()

    def cycle_verb(self) -> None:
        verbs = [verb for verb in Verb]
        index = verbs.index(self.selected_verb)
        self.selected_verb = verbs[(index + 1) % len(verbs)]

    def handle_left_click(self, position: Tuple[int, int]) -> None:
        if position[1] <= self.verb_bar.height:
            result = self.verb_bar.handle_click(position)
            if result is None:
                return
            action, value = result
            if action == "verb":
                self.selected_verb = value  # type: ignore[assignment]
            elif action == "inventory":
                self.inventory_window.toggle()
            elif action == "options":
                self.message_window.show("Options are not implemented yet.")
            return

        if self.inventory_window.visible:
            selection = self.inventory_window.handle_click(position, self.inventory)
            if selection:
                self.selected_item_id = selection
                item = self.inventory.get_item(selection)
                if item:
                    self.message_window.show(f"{item.name}: {item.description}")
            return

        if self.selected_verb == Verb.WALK:
            self.handle_walk_click(position)
        else:
            self.handle_verb_click(position)

    def handle_walk_click(self, position: Tuple[int, int]) -> None:
        room = self.current_room
        hotspot = room.find_hotspot(position)
        if hotspot:
            action_data = hotspot.get_action("walk")
            if action_data:
                self.queue_hotspot_action(hotspot, Verb.WALK, action_data)
                return
        self.move_hero_to(position)

    def move_hero_to(self, destination: Vector2) -> None:
        pathfinder = self.current_room.pathfinder
        self.hero.set_destination(destination, pathfinder)
        if not self.hero.path and not self.hero.has_reached(destination):
            self.message_window.show("You can't walk there.")

    def handle_verb_click(self, position: Tuple[int, int]) -> None:
        room = self.current_room
        hotspot = room.find_hotspot(position)
        if not hotspot:
            self.message_window.show("Nothing of interest there.")
            return
        verb_name = self.selected_verb.name.lower()
        action_data = hotspot.get_action(verb_name)
        if not action_data:
            self.message_window.show("That has no effect.")
            return
        self.queue_hotspot_action(hotspot, self.selected_verb, action_data)

    def queue_hotspot_action(self, hotspot: Hotspot, verb: Verb, action_data: object) -> None:
        target_point = hotspot.walk_to if hotspot.walk_to else hotspot.rect.center
        self.pending_action = PendingAction(hotspot, verb, target_point, action_data)
        self.move_hero_to(target_point)
        if not self.hero.path and not self.hero.has_reached(target_point):
            self.pending_action = None
            return
        if self.hero.has_reached(target_point):
            self.execute_pending_action()

    def execute_pending_action(self) -> None:
        if not self.pending_action:
            return
        action = self.pending_action
        if not self.hero.has_reached(action.target_point):
            return
        self.pending_action = None
        self.perform_action(action.hotspot, action.verb, action.action_data)

    def perform_action(self, hotspot: Hotspot, verb: Verb, action_data: object) -> None:
        if isinstance(action_data, str):
            self.message_window.show(action_data)
            return
        if not isinstance(action_data, dict):
            self.message_window.show("Nothing happens.")
            return

        if not self._check_conditions(action_data):
            failure = action_data.get("failure_message", "That won't work.")
            self.message_window.show(failure)
            return

        requires_item = action_data.get("requires_item")
        if requires_item and action_data.get("consume_item", False):
            self.inventory.remove_item(requires_item)
            if self.selected_item_id == requires_item:
                self.selected_item_id = None

        gives_item = action_data.get("gives_item")
        if gives_item and gives_item in self.items_catalog and not self.inventory.has_item(gives_item):
            self.inventory.add_item(self.items_catalog[gives_item])
            message = action_data.get("message", f"You picked up {self.items_catalog[gives_item].name}.")
        else:
            message = action_data.get("message")

        set_flag = action_data.get("set_flag")
        if set_flag:
            if isinstance(set_flag, list):
                self.flags.update(set_flag)
            else:
                self.flags.add(set_flag)
        clear_flag = action_data.get("clear_flag")
        if clear_flag:
            if isinstance(clear_flag, list):
                for flag in clear_flag:
                    self.flags.discard(flag)
            else:
                self.flags.discard(clear_flag)

        if message:
            self.message_window.show(message)

        room_change = action_data.get("room")
        if room_change:
            entry_point = action_data.get("entry_point")
            if isinstance(entry_point, str):
                self.change_room(room_change, entry_point)
            elif isinstance(entry_point, (list, tuple)):
                self.change_room(room_change, tuple(entry_point))
            else:
                self.change_room(room_change, None)

    def _check_conditions(self, action_data: dict) -> bool:
        required_flag = action_data.get("requires_flag")
        if required_flag and required_flag not in self.flags:
            return False
        forbidden_flag = action_data.get("requires_flag_not")
        if forbidden_flag and forbidden_flag in self.flags:
            return False
        required_item = action_data.get("requires_item")
        if required_item:
            require_selected = action_data.get("requires_selected", True)
            if require_selected:
                if self.selected_item_id != required_item:
                    return False
            else:
                if not (self.inventory.has_item(required_item) or self.selected_item_id == required_item):
                    return False
        return True

    def change_room(self, room_id: str, entry_point: Optional[object]) -> None:
        if room_id not in self.rooms:
            self.message_window.show("That path is blocked.")
            return
        self.current_room_id = room_id
        room = self.current_room
        if isinstance(entry_point, tuple):
            self.hero.position = pygame.math.Vector2(entry_point)
        else:
            self.hero.position = pygame.math.Vector2(room.get_entry_point(entry_point if isinstance(entry_point, str) else None))
        self.hero.set_path([])
        self.pending_action = None
        self.inventory_window.hide()
        self.message_window.show(f"You enter {room.name}.")

    def update(self, dt: float) -> None:
        self.hero.update(dt)
        for zombie in self.zombies.get(self.current_room_id, []):
            zombie.update(dt, (self.hero.position.x, self.hero.position.y), self.current_room.pathfinder)
        self.execute_pending_action()
        self.message_window.update(dt)
        self.zombie_warning_timer = max(0.0, self.zombie_warning_timer - dt)
        for zombie in self.zombies.get(self.current_room_id, []):
            if self.hero.position.distance_to(zombie.position) < 14 and self.zombie_warning_timer <= 0:
                self.message_window.show("A zombie groans nearby!")
                self.zombie_warning_timer = 4.0
                break

    def draw(self) -> None:
        room = self.current_room
        self.screen.blit(room.background, (0, 0))
        characters = []
        characters.append((self.hero.position.y, self.hero, self._compute_scale(self.hero)))
        for zombie in self.zombies.get(self.current_room_id, []):
            characters.append((zombie.position.y, zombie, self._compute_scale(zombie)))
        characters.sort(key=lambda entry: entry[0])
        for _, character, scale in characters:
            rect = character.draw(self.screen, scale)
            foot_pos = (int(character.position.x), min(self.height - 1, int(character.position.y)))
            if room.priority_mask.get_at(foot_pos)[0] > 200:
                self.screen.blit(room.walkbehind_overlay, (0, 0), rect)
        selected_item = self.inventory.get_item(self.selected_item_id) if self.selected_item_id else None
        self.verb_bar.draw(self.screen, self.selected_verb, selected_item)
        self.inventory_window.draw(self.screen, self.inventory, self.selected_item_id)
        self.message_window.draw(self.screen)
        cursor_surface = self.verb_bar.get_cursor_surface(self.selected_verb)
        cursor_pos = pygame.mouse.get_pos()
        cursor_rect = cursor_surface.get_rect()
        cursor_rect.topleft = cursor_pos
        self.screen.blit(cursor_surface, cursor_rect)
        pygame.display.flip()

    def _compute_scale(self, character) -> float:
        min_y, max_y = self.current_room.walk_bounds
        denominator = max(1.0, max_y - min_y)
        ratio = (character.position.y - min_y) / denominator
        ratio = max(0.0, min(1.0, ratio))
        return character.min_scale + (character.max_scale - character.min_scale) * ratio
