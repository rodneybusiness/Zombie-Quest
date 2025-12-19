"""Parallax background system - multi-layer depth with camera movement.

Splits backgrounds into foreground, midground, and background layers that
scroll at different speeds for authentic depth perception.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
import pygame

Position = Tuple[float, float]


@dataclass
class ParallaxLayer:
    """A single parallax layer with its own depth and scroll speed."""
    surface: pygame.Surface  # The layer image
    depth: float  # 0.0 (far background) to 1.0 (foreground)
    scroll_factor: float  # Multiplier for camera movement (0.0 to 1.0)
    offset_x: float = 0.0  # Current scroll offset
    offset_y: float = 0.0
    wrap_horizontal: bool = False  # Whether layer wraps horizontally
    wrap_vertical: bool = False  # Whether layer wraps vertically


class ParallaxBackground:
    """Manages multiple parallax layers for depth effect.

    Layers scroll at different speeds based on depth to create
    a pseudo-3D effect as the camera moves.
    """

    def __init__(self, screen_size: Tuple[int, int]) -> None:
        self.screen_size = screen_size
        self.layers: List[ParallaxLayer] = []
        self.camera_position = pygame.Vector2(0, 0)
        self.previous_camera_position = pygame.Vector2(0, 0)

    def add_layer(self, layer: ParallaxLayer) -> None:
        """Add a parallax layer.

        Layers are automatically sorted by depth (far to near).
        """
        self.layers.append(layer)
        # Sort by depth (far layers first)
        self.layers.sort(key=lambda l: l.depth)

    def clear_layers(self) -> None:
        """Remove all layers."""
        self.layers.clear()

    def update(self, camera_position: Position, dt: float = 0.0) -> None:
        """Update parallax offsets based on camera movement.

        Args:
            camera_position: (x, y) camera position in world space
            dt: Delta time (unused, kept for consistency)
        """
        self.previous_camera_position = self.camera_position.copy()
        self.camera_position = pygame.Vector2(camera_position)

        # Calculate camera delta
        delta = self.camera_position - self.previous_camera_position

        # Update each layer's offset
        for layer in self.layers:
            # Scroll based on depth (far layers move less)
            layer.offset_x += delta.x * layer.scroll_factor
            layer.offset_y += delta.y * layer.scroll_factor

            # Handle wrapping
            if layer.wrap_horizontal:
                layer_width = layer.surface.get_width()
                layer.offset_x = layer.offset_x % layer_width

            if layer.wrap_vertical:
                layer_height = layer.surface.get_height()
                layer.offset_y = layer.offset_y % layer_height

    def render(self, surface: pygame.Surface) -> None:
        """Render all parallax layers in order (back to front)."""
        for layer in self.layers:
            self._render_layer(surface, layer)

    def _render_layer(self, surface: pygame.Surface, layer: ParallaxLayer) -> None:
        """Render a single parallax layer."""
        layer_w, layer_h = layer.surface.get_size()
        screen_w, screen_h = self.screen_size

        # Calculate render position
        x = -layer.offset_x
        y = -layer.offset_y

        if layer.wrap_horizontal or layer.wrap_vertical:
            # Tiled rendering for wrapped layers
            start_x = int(x) % layer_w - layer_w
            start_y = int(y) % layer_h - layer_h

            tiles_x = (screen_w // layer_w) + 2
            tiles_y = (screen_h // layer_h) + 2

            for ty in range(tiles_y):
                for tx in range(tiles_x):
                    pos = (start_x + tx * layer_w, start_y + ty * layer_h)
                    surface.blit(layer.surface, pos)
        else:
            # Single blit for non-wrapped layers
            surface.blit(layer.surface, (int(x), int(y)))


def split_background_into_layers(
    background_generator: Callable,
    room_id: str,
    size: Tuple[int, int] = (320, 200),
) -> List[ParallaxLayer]:
    """Split a background into parallax layers.

    This function takes an existing background and creates depth layers.
    For new backgrounds, you'd create layers directly.

    Args:
        background_generator: Function that creates the background
        room_id: Room identifier
        size: Background size

    Returns:
        List of ParallaxLayer objects
    """
    layers = []

    if room_id == "hennepin_outside":
        # Layer 0: Far city skyline (slowest)
        far_layer = _create_hennepin_far_layer(size)
        layers.append(ParallaxLayer(
            surface=far_layer,
            depth=0.0,
            scroll_factor=0.1,
            wrap_horizontal=True,
        ))

        # Layer 1: Mid buildings and street
        mid_layer = _create_hennepin_mid_layer(size)
        layers.append(ParallaxLayer(
            surface=mid_layer,
            depth=0.5,
            scroll_factor=0.5,
        ))

        # Layer 2: Foreground details (fastest)
        fore_layer = _create_hennepin_fore_layer(size)
        layers.append(ParallaxLayer(
            surface=fore_layer,
            depth=1.0,
            scroll_factor=1.0,
        ))

    elif room_id == "record_store":
        # Indoor scenes have less parallax but still benefit from depth
        # Layer 0: Back wall with posters
        back_layer = _create_record_store_back_layer(size)
        layers.append(ParallaxLayer(
            surface=back_layer,
            depth=0.0,
            scroll_factor=0.2,
        ))

        # Layer 1: Record bins
        mid_layer = _create_record_store_mid_layer(size)
        layers.append(ParallaxLayer(
            surface=mid_layer,
            depth=0.5,
            scroll_factor=0.6,
        ))

        # Layer 2: Counter and foreground
        fore_layer = _create_record_store_fore_layer(size)
        layers.append(ParallaxLayer(
            surface=fore_layer,
            depth=1.0,
            scroll_factor=1.0,
        ))

    else:
        # Default: single layer (no parallax)
        bg = background_generator(size)
        layers.append(ParallaxLayer(
            surface=bg,
            depth=1.0,
            scroll_factor=1.0,
        ))

    return layers


# Layer creation functions for Hennepin Avenue
def _create_hennepin_far_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Create far background layer (distant skyline)."""
    from .backgrounds import create_gradient, draw_stars, draw_building_silhouette
    import random

    surface = pygame.Surface(size)
    w, h = size

    # Night sky
    create_gradient(surface, [
        (10, 5, 30),
        (30, 15, 60),
        (50, 25, 80),
    ])

    # Stars
    draw_stars(surface, 50)

    # Distant buildings
    for i in range(8):
        bx = i * 50 - 20
        bw = random.randint(30, 50)
        bh = random.randint(30, 60)
        draw_building_silhouette(surface, bx, bw, bh, (20, 15, 40), windows=True)

    return surface


def _create_hennepin_mid_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Create mid layer (main buildings, street)."""
    from .backgrounds import draw_building_silhouette, draw_neon_sign
    import math

    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    # First Avenue building
    building_x = 160
    building_w = 100
    building_h = 130
    building_y = h - building_h - 50

    pygame.draw.rect(surface, (35, 30, 50), (building_x, building_y, building_w, building_h))

    # Star
    star_x, star_y = building_x + building_w // 2, building_y + 20
    star_color = (255, 255, 200)
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        x1 = star_x + int(12 * math.cos(angle))
        y1 = star_y + int(12 * math.sin(angle))
        pygame.draw.line(surface, star_color, (star_x, star_y), (x1, y1), 2)

    # Record store
    store_x = 40
    pygame.draw.rect(surface, (50, 45, 70), (store_x, h - 140, 80, 90))

    # Street
    pygame.draw.rect(surface, (25, 25, 40), (0, h - 55, w, 60))

    return surface


def _create_hennepin_fore_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Create foreground layer (kiosk, lamp posts)."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    # Poster kiosk (close to camera)
    kiosk_x = 15
    pygame.draw.rect(surface, (60, 55, 75), (kiosk_x, h - 110, 20, 60))

    # Street light poles
    for lx in [80, 200, 290]:
        pygame.draw.rect(surface, (60, 60, 70), (lx, h - 140, 4, 90))

    return surface


# Layer creation for record store
def _create_record_store_back_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Record store back wall."""
    from .backgrounds import create_gradient

    surface = pygame.Surface(size)
    w, h = size

    create_gradient(surface, [
        (50, 30, 70),
        (70, 45, 100),
        (40, 25, 55),
    ])

    # Back wall
    wall_y = 30
    floor_y = h - 50
    pygame.draw.rect(surface, (80, 70, 100), (0, wall_y, w, floor_y - wall_y))

    # Posters (static on wall)
    poster_data = [
        (20, 45, (255, 200, 80)),
        (100, 50, (100, 200, 255)),
        (220, 42, (255, 150, 100)),
    ]
    for px, py, color in poster_data:
        pygame.draw.rect(surface, color, (px, py, 35, 45))

    return surface


def _create_record_store_mid_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Record store middle layer (bins)."""
    import random

    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    floor_y = h - 50
    bin_y = floor_y - 50

    # Record bins
    for bx in [30, 100, 170, 240]:
        pygame.draw.rect(surface, (50, 40, 55), (bx, bin_y, 55, 50))
        # Records
        for i in range(8):
            rx = bx + 5 + i * 6
            color = random.choice([
                (200, 180, 160), (180, 160, 140), (220, 200, 180)
            ])
            pygame.draw.rect(surface, color, (rx, bin_y + 8, 4, 38))

    return surface


def _create_record_store_fore_layer(size: Tuple[int, int]) -> pygame.Surface:
    """Record store foreground (counter, booth)."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    floor_y = h - 50

    # Counter
    counter_x = w - 90
    pygame.draw.rect(surface, (70, 55, 65), (counter_x, floor_y - 45, 80, 45))

    # Listening booth
    booth_x = 10
    pygame.draw.rect(surface, (40, 35, 55), (booth_x, floor_y - 90, 60, 90))

    # Floor
    pygame.draw.rect(surface, (60, 50, 45), (0, floor_y, w, 55))

    return surface


"""
INTEGRATION EXAMPLE - Add to zombie_quest/engine.py or room system:

from .parallax_backgrounds import ParallaxBackground, split_background_into_layers
from .backgrounds import get_room_background

class Room:
    def __init__(self, room_id, size=(320, 200)):
        self.room_id = room_id

        # Create parallax background system
        self.parallax = ParallaxBackground(size)

        # Generate and add layers
        from .backgrounds import create_hennepin_background  # Or appropriate generator
        layers = split_background_into_layers(
            create_hennepin_background,
            room_id,
            size
        )

        for layer in layers:
            self.parallax.add_layer(layer)

    def update(self, camera_position, dt):
        '''Update room with camera position.'''
        self.parallax.update(camera_position, dt)

    def render(self, surface):
        '''Render room background.'''
        self.parallax.render(surface)

# Camera follows player
class GameEngine:
    def update(self, dt):
        # ... game logic ...

        # Camera follows hero
        camera_x = self.hero.position.x
        camera_y = self.hero.position.y

        # Update parallax backgrounds
        self.current_room.update((camera_x, camera_y), dt)

    def render(self):
        # Render parallax background
        self.current_room.render(self.screen)

        # Render characters on top
        # ... character rendering ...
"""
