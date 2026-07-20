import json
import os
from dataclasses import dataclass

import pygame
from typing import Dict, List, Optional, Tuple

Color = Tuple[int, int, int]

DEFAULT_BG_COLOR: Color = (40, 60, 80)
DEFAULT_PRIORITY_WHITE: Color = (255, 255, 255)
DEFAULT_PRIORITY_BLACK: Color = (0, 0, 0)


@dataclass(frozen=True)
class RoomAssets:
    """Authored art for one room, loaded from assets/rooms/<id>/."""
    background: pygame.Surface
    priority_mask: Optional[pygame.Surface]
    emissive: Optional[pygame.Surface]


@dataclass(frozen=True)
class CharacterSet:
    """Authored animation set loaded from assets/characters/<name>/."""
    animations: Dict[str, List[pygame.Surface]]
    frame_size: Tuple[int, int]
    anchor: Tuple[int, int]
    animation_map: Dict[str, dict]
    perspective_steps: Tuple[float, ...]


def load_image(path: str, *, alpha: bool = False,
               validate_palette: bool = True,
               expected_size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """Load a PNG, optionally validating size and the ZQ-32 contract.

    convert()/convert_alpha() only runs when a display exists, so unit
    tests without set_mode still work (surfaces are just unconverted).
    """
    surface = pygame.image.load(path)
    if expected_size and surface.get_size() != expected_size:
        raise ValueError(f"{path}: size {surface.get_size()}, expected {expected_size}")
    if validate_palette:
        from .palette import assert_surface_palette
        assert_surface_palette(surface, context=path)
    if pygame.display.get_surface() is not None:
        surface = surface.convert_alpha() if alpha else surface.convert()
    return surface


def load_room_assets(assets_root: str, room_id: str,
                     expected_size: Tuple[int, int] = (320, 200)) -> Optional[RoomAssets]:
    """Load a room's painted art, or None when the room has no assets yet
    (caller falls back to the procedural generator - per-room migration)."""
    room_dir = os.path.join(assets_root, "rooms", room_id)
    bg_path = os.path.join(room_dir, "bg.png")
    if not os.path.exists(bg_path):
        return None
    background = load_image(bg_path, expected_size=expected_size)

    priority_path = os.path.join(room_dir, "priority.png")
    priority_mask = None
    if os.path.exists(priority_path):
        priority_mask = load_image(priority_path, validate_palette=False,
                                   expected_size=expected_size)

    emissive_path = os.path.join(room_dir, "emissive.png")
    emissive = None
    if os.path.exists(emissive_path):
        emissive = load_image(emissive_path, alpha=True, expected_size=expected_size)

    return RoomAssets(background=background, priority_mask=priority_mask,
                      emissive=emissive)


def load_character_set(assets_root: str, name: str) -> Optional[CharacterSet]:
    """Load sheet.png + meta.json for a character, or None if absent
    (caller falls back to procedural sprite generation)."""
    char_dir = os.path.join(assets_root, "characters", name)
    sheet_path = os.path.join(char_dir, "sheet.png")
    meta_path = os.path.join(char_dir, "meta.json")
    if not (os.path.exists(sheet_path) and os.path.exists(meta_path)):
        return None
    with open(meta_path, encoding="utf-8") as handle:
        meta = json.load(handle)
    sheet = load_image(sheet_path, alpha=True)

    frame_w, frame_h = meta["frame_size"]
    directions = meta["directions"]
    frames_per_direction = sheet.get_width() // frame_w
    animations: Dict[str, List[pygame.Surface]] = {}
    for row, direction in enumerate(directions):
        frames = []
        for col in range(frames_per_direction):
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h))
            frames.append(frame)
        animations[direction] = frames

    return CharacterSet(
        animations=animations,
        frame_size=(frame_w, frame_h),
        anchor=tuple(meta["anchor"]),
        animation_map=meta.get("animations", {}),
        perspective_steps=tuple(meta.get("perspective_steps", (1.0,))),
    )


def ensure_font_initialized() -> None:
    if not pygame.font.get_init():
        pygame.font.init()


def load_serif_font(size: int) -> pygame.font.Font:
    """UI font: pygame's bundled font, identical on every OS and CI runner.

    System-font matching made text render differently per machine, which
    breaks golden-frame testing; rendered with antialias=False everywhere
    so text stays two-color and palette-safe. (Name kept for existing
    call sites; a period bitmap font replaces this in the UI art pass.)
    """
    ensure_font_initialized()
    return pygame.font.Font(None, size)


def create_placeholder_surface(
    size: Tuple[int, int],
    fill_color: Color,
    label: str,
    border_color: Color = (10, 10, 10),
    text_color: Color = (240, 240, 240),
) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(fill_color)
    pygame.draw.rect(surface, border_color, surface.get_rect(), 2)
    font = load_serif_font(max(8, size[1] // 4))
    text_surface = font.render(label, True, text_color)
    text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
    surface.blit(text_surface, text_rect)
    return surface


def _shift_color(color: Color, delta: int) -> Color:
    return tuple(max(0, min(255, c + delta)) for c in color)


def create_directional_animation(
    base_name: str,
    base_color: Color,
    frame_size: Tuple[int, int],
    frame_count: int = 4,
) -> Dict[str, List[pygame.Surface]]:
    directions = ["down", "up", "left", "right"]
    animations: Dict[str, List[pygame.Surface]] = {}
    for direction_index, direction in enumerate(directions):
        direction_frames: List[pygame.Surface] = []
        for frame in range(frame_count):
            color_shift = direction_index * 15 + frame * 8
            color = _shift_color(base_color, color_shift)
            label = f"{base_name} {direction.title()} {frame + 1}"
            frame_surface = create_placeholder_surface(frame_size, color, label)
            direction_frames.append(frame_surface)
        animations[direction] = direction_frames
    return animations


def _normalize_color(color: Tuple[int, int, int]) -> Color:
    return tuple(max(0, min(255, int(component))) for component in color)


def _draw_gradient(surface: pygame.Surface, colors: List[Color]) -> None:
    width, height = surface.get_size()
    steps = len(colors) - 1
    if steps <= 0:
        surface.fill(colors[0] if colors else DEFAULT_BG_COLOR)
        return
    for y in range(height):
        ratio = y / max(1, height - 1)
        segment = min(int(ratio * steps), steps - 1)
        local_ratio = ratio * steps - segment
        start = colors[segment]
        end = colors[segment + 1]
        color = (
            int(start[0] + (end[0] - start[0]) * local_ratio),
            int(start[1] + (end[1] - start[1]) * local_ratio),
            int(start[2] + (end[2] - start[2]) * local_ratio),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))


def create_placeholder_background(
    label: str,
    size: Tuple[int, int] = (320, 200),
    base_color: Color = DEFAULT_BG_COLOR,
    gradient: Optional[List[Color]] = None,
    accent_lines: Optional[List[Dict[str, object]]] = None,
    overlay_shapes: Optional[List[Dict]] = None,
    label_color: Color = (240, 240, 210),
) -> pygame.Surface:
    surface = pygame.Surface(size)
    width, height = size
    if gradient:
        normalized = [_normalize_color(color) for color in gradient]
        _draw_gradient(surface, normalized)
    else:
        default_gradient = [
            _normalize_color(tuple(component * 0.7 for component in base_color)),
            _normalize_color(base_color),
        ]
        _draw_gradient(surface, default_gradient)
    if accent_lines:
        for line in accent_lines:
            y = int(line.get("y", 0))
            line_height = max(1, int(line.get("height", 1)))
            color = _normalize_color(tuple(line.get("color", (255, 255, 255))))
            rect = pygame.Rect(0, max(0, y), width, line_height)
            surface.fill(color, rect)
    if overlay_shapes:
        for shape in overlay_shapes:
            color = _normalize_color(tuple(shape.get("color", (255, 255, 255))))
            if shape.get("shape") == "rect":
                rect = pygame.Rect(shape.get("rect", [0, 0, width, height]))
                pygame.draw.rect(surface, color, rect)
            elif shape.get("shape") == "polygon":
                points = [tuple(point) for point in shape.get("points", [])]
                if len(points) >= 3:
                    pygame.draw.polygon(surface, color, points)
            elif shape.get("shape") == "circle":
                center = tuple(shape.get("center", (0, 0)))
                radius = int(shape.get("radius", 0))
                pygame.draw.circle(surface, color, center, radius)
    font = load_serif_font(20)
    text_surface = font.render(label, True, label_color)
    text_rect = text_surface.get_rect(center=(width // 2, 24))
    shadow_surface = font.render(label, True, (0, 0, 0))
    surface.blit(shadow_surface, text_rect.move(2, 2))
    surface.blit(text_surface, text_rect)
    return surface


def create_mask_from_shapes(
    size: Tuple[int, int],
    shapes: List[Dict],
    foreground: Color,
    background: Color,
) -> pygame.Surface:
    surface = pygame.Surface(size)
    surface.fill(background)
    for shape in shapes:
        if shape.get("shape") == "rect":
            rect = pygame.Rect(shape["rect"])
            pygame.draw.rect(surface, foreground, rect)
        elif shape.get("shape") == "polygon":
            points = [tuple(point) for point in shape.get("points", [])]
            if len(points) >= 3:
                pygame.draw.polygon(surface, foreground, points)
        elif shape.get("shape") == "circle":
            center = tuple(shape.get("center", (0, 0)))
            radius = int(shape.get("radius", 0))
            pygame.draw.circle(surface, foreground, center, radius)
    return surface


def create_priority_mask(
    size: Tuple[int, int],
    regions: List[Dict],
    foreground: Color = DEFAULT_PRIORITY_WHITE,
    background: Color = DEFAULT_PRIORITY_BLACK,
) -> pygame.Surface:
    return create_mask_from_shapes(size, regions, foreground, background)


def create_walkable_mask(
    size: Tuple[int, int],
    zones: List[Dict],
    foreground: Color = (255, 255, 255),
    background: Color = (0, 0, 0),
) -> pygame.Surface:
    return create_mask_from_shapes(size, zones, foreground, background)


def create_ui_icon(label: str, size: Tuple[int, int], color: Color) -> pygame.Surface:
    return create_placeholder_surface(size, color, label, border_color=(20, 20, 20), text_color=(250, 250, 250))


def build_priority_overlay(background: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    """Copy background pixels where the priority mask is (near-)white.

    Threshold matches Room.is_behind (channels > 200) rather than exact white,
    and runs through pygame.mask at C speed instead of per-pixel Python.
    """
    bitmask = pygame.mask.from_threshold(mask, (255, 255, 255), (60, 60, 60))
    size = background.get_size()
    source = pygame.Surface(size, pygame.SRCALPHA, 32)
    source.blit(background, (0, 0))
    destination = pygame.Surface(size, pygame.SRCALPHA, 32)
    return bitmask.to_surface(surface=destination, setsurface=source, unsetcolor=(0, 0, 0, 0))


# Backwards-compatible name used by existing tests.
extract_priority_overlay = build_priority_overlay
