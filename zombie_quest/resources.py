import pygame
from typing import List, Tuple, Dict

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


def create_placeholder_background(
    label: str,
    size: Tuple[int, int] = (320, 200),
    base_color: Color = DEFAULT_BG_COLOR,
) -> pygame.Surface:
    surface = pygame.Surface(size)
    width, height = size
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(base_color[0] * (0.7 + 0.3 * ratio)),
            int(base_color[1] * (0.7 + 0.3 * ratio)),
            int(base_color[2] * (0.7 + 0.3 * ratio)),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    font = load_serif_font(20)
    text_surface = font.render(label, True, (240, 240, 210))
    text_rect = text_surface.get_rect(center=(width // 2, 24))
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
