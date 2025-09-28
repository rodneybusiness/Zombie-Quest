import pygame
from typing import Dict, List, Optional, Tuple

Color = Tuple[int, int, int]

DEFAULT_BG_COLOR: Color = (40, 60, 80)
DEFAULT_PRIORITY_WHITE: Color = (255, 255, 255)
DEFAULT_PRIORITY_BLACK: Color = (0, 0, 0)


def ensure_font_initialized() -> None:
    if not pygame.font.get_init():
        pygame.font.init()


def load_serif_font(size: int) -> pygame.font.Font:
    ensure_font_initialized()
    preferred = ["Times New Roman", "Georgia", "Book Antiqua", "serif"]
    font_path = pygame.font.match_font(preferred)
    if font_path:
        return pygame.font.Font(font_path, size)
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


def extract_priority_overlay(background: pygame.Surface, mask: pygame.Surface) -> pygame.Surface:
    width, height = background.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    white = DEFAULT_PRIORITY_WHITE
    for y in range(height):
        for x in range(width):
            if mask.get_at((x, y))[:3] == white:
                overlay.set_at((x, y), background.get_at((x, y)))
            else:
                overlay.set_at((x, y), (0, 0, 0, 0))
    return overlay
