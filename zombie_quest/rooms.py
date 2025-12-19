from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

from .characters import Hero, Zombie, ZombieSpawner
from .pathfinding import GridPathfinder
from .resources import (
    DEFAULT_BG_COLOR,
    create_placeholder_background,
    create_priority_mask,
    create_walkable_mask,
    extract_priority_overlay,
)

RoomSize = Tuple[int, int]
VerbMessages = Dict[str, str]


@dataclass
class Hotspot:
    rect: pygame.Rect
    name: str
    verbs: VerbMessages
    walk_position: Optional[Tuple[int, int]] = None
    required_item: Optional[str] = None
    give_item: Optional[str] = None
    remove_item: Optional[str] = None
    talk_target: Optional[str] = None
    target_room: Optional[str] = None
    target_position: Optional[Tuple[int, int]] = None
    transition_verb: str = "use"
    requires_success_for_transition: bool = False
    transition_message: Optional[str] = None
    give_item_triggers: Tuple[str, ...] = ("use",)
    remove_item_triggers: Tuple[str, ...] = ("use",)

    def message_for(self, verb: str, outcome: str = "default") -> str:
        if outcome and outcome != "default":
            key = f"{verb}_{outcome}"
            if key in self.verbs:
                return self.verbs[key]
        default_key = f"{verb}_default"
        if default_key in self.verbs:
            return self.verbs[default_key]
        return self.verbs.get(verb, "Nothing happens.")


class Room:
    def __init__(self, data: Dict) -> None:
        self.id = data["id"]
        self.name = data.get("name", self.id.title())
        self.size: RoomSize = tuple(data.get("size", (320, 200)))  # type: ignore[assignment]
        background_config = data.get("background")
        if isinstance(background_config, dict):
            gradient = background_config.get("gradient")
            gradient_colors: Optional[List[Tuple[int, int, int]]] = None
            if isinstance(gradient, list) and gradient:
                gradient_colors = []
                for color in gradient:
                    if isinstance(color, (list, tuple)) and len(color) >= 3:
                        gradient_colors.append((int(color[0]), int(color[1]), int(color[2])))
            accent_lines = background_config.get("accent_lines")
            processed_lines: Optional[List[Dict[str, object]]] = None
            if isinstance(accent_lines, list):
                processed_lines = []
                for entry in accent_lines:
                    line: Dict[str, object] = {}
                    for key in ("y", "height"):
                        if key in entry:
                            line[key] = int(entry[key])
                    if "color" in entry:
                        color_value = entry["color"]
                        if isinstance(color_value, (list, tuple)) and len(color_value) >= 3:
                            color = (int(color_value[0]), int(color_value[1]), int(color_value[2]))
                        else:
                            color = (255, 255, 255)
                    else:
                        color = (255, 255, 255)
                    line["color"] = color
                    processed_lines.append(line)
            overlay_shapes = background_config.get("shapes")
            processed_shapes: Optional[List[Dict]] = None
            if isinstance(overlay_shapes, list):
                processed_shapes = []
                for shape in overlay_shapes:
                    processed_shape = dict(shape)
                    if "color" in processed_shape:
                        color_value = processed_shape["color"]
                        if isinstance(color_value, (list, tuple)) and len(color_value) >= 3:
                            processed_shape["color"] = (
                                int(color_value[0]),
                                int(color_value[1]),
                                int(color_value[2]),
                            )
                        else:
                            processed_shape["color"] = (255, 255, 255)
                    processed_shapes.append(processed_shape)
            label = background_config.get("label", data.get("background_label", self.name))
            base_color_value = background_config.get("base_color", DEFAULT_BG_COLOR)
            if isinstance(base_color_value, (list, tuple)) and len(base_color_value) >= 3:
                base_color = (
                    int(base_color_value[0]),
                    int(base_color_value[1]),
                    int(base_color_value[2]),
                )
            else:
                base_color = DEFAULT_BG_COLOR
            label_color_value = background_config.get("label_color", (240, 240, 210))
            if isinstance(label_color_value, (list, tuple)) and len(label_color_value) >= 3:
                label_color = (
                    int(label_color_value[0]),
                    int(label_color_value[1]),
                    int(label_color_value[2]),
                )
            else:
                label_color = (240, 240, 210)
            self.background = create_placeholder_background(
                label,
                self.size,
                base_color=base_color,
                gradient=gradient_colors,
                accent_lines=processed_lines,
                overlay_shapes=processed_shapes,
                label_color=label_color,
            )
        else:
            self.background = create_placeholder_background(data.get("background_label", self.name), self.size)
        self.priority_mask = create_priority_mask(self.size, data.get("priority_regions", []))
        self.walkable_mask = create_walkable_mask(self.size, data.get("walkable_zones", []))
        self.priority_overlay = extract_priority_overlay(self.background, self.priority_mask)
        self.pathfinder = GridPathfinder(self.walkable_mask)
        self.bounds = pygame.Rect((0, 0), self.size)
        self.hotspots: List[Hotspot] = [self._create_hotspot(h) for h in data.get("hotspots", [])]
        self.zombies: List[Zombie] = ZombieSpawner.create_zombies_for_room(data.get("zombies", []), self.id)
        self.entry_message = data.get("entry_message")
        default_entry = data.get("default_entry")
        if default_entry:
            self.default_entry: Tuple[int, int] = (int(default_entry[0]), int(default_entry[1]))
        else:
            self.default_entry = (self.size[0] // 2, int(self.size[1] * 0.8))

    def _create_hotspot(self, data: Dict) -> Hotspot:
        rect = pygame.Rect(data.get("rect", [0, 0, 10, 10]))
        verbs: VerbMessages = data.get("verbs", {})
        walk_position = tuple(data.get("walk_position")) if data.get("walk_position") else None
        return Hotspot(
            rect=rect,
            name=data.get("name", "Hotspot"),
            verbs=verbs,
            walk_position=walk_position,
            required_item=data.get("required_item"),
            give_item=data.get("give_item"),
            remove_item=data.get("remove_item"),
            talk_target=data.get("talk_target"),
            target_room=data.get("target_room"),
            target_position=tuple(data.get("target_position")) if data.get("target_position") else None,
            transition_verb=(data.get("transition_verb") or "use").lower(),
            requires_success_for_transition=bool(data.get("requires_success_for_transition", False)),
            transition_message=data.get("transition_message"),
            give_item_triggers=tuple(trigger.lower() for trigger in data.get("give_item_triggers", ["use"])),
            remove_item_triggers=tuple(trigger.lower() for trigger in data.get("remove_item_triggers", ["use"])),
        )

    def update(self, dt: float, hero: Hero) -> None:
        hero_position = hero.foot_position
        for zombie in self.zombies:
            zombie.update(dt, hero_position, self.bounds)

    def draw(self, surface: pygame.Surface, hero: Hero) -> None:
        surface.blit(self.background, (0, 0))
        characters: List = self.zombies + [hero]
        characters.sort(key=lambda c: c.position.y)
        hero_rect: Optional[pygame.Rect] = None
        hero_behind = False
        for character in characters:
            rect = character.draw(surface, self.size[1])
            if character is hero:
                hero_rect = rect
                hero_behind = self.is_behind(character.foot_position)
        if hero_behind and hero_rect:
            overlay_rect = hero_rect.clip(self.priority_overlay.get_rect())
            if overlay_rect.width > 0 and overlay_rect.height > 0:
                surface.blit(self.priority_overlay, overlay_rect.topleft, overlay_rect)

    def is_walkable(self, position: Tuple[float, float]) -> bool:
        x, y = int(position[0]), int(position[1])
        if not self.bounds.collidepoint(x, y):
            return False
        if not self.walkable_mask:
            return True  # Default to walkable if mask missing
        try:
            color = self.walkable_mask.get_at((x, y))
            return color[0] > 0 or color[1] > 0 or color[2] > 0
        except IndexError:
            return True

    def is_behind(self, position: Tuple[float, float]) -> bool:
        x, y = int(position[0]), int(position[1])
        if not self.bounds.collidepoint(x, y):
            return False
        if not self.priority_mask:
            return False  # Default to not behind if mask missing
        try:
            color = self.priority_mask.get_at((x, y))
            return color[0] > 200 and color[1] > 200 and color[2] > 200
        except IndexError:
            return False

    def find_hotspot(self, position: Tuple[int, int]) -> Optional[Hotspot]:
        for hotspot in self.hotspots:
            if hotspot.rect.collidepoint(position):
                return hotspot
        return None
