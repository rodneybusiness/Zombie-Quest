"""Drop shadow rendering system for characters.

Provides proper visual grounding with soft, perspective-correct shadows.
Integrates seamlessly with existing character rendering.
"""
from __future__ import annotations

from typing import Tuple
import pygame

from .sprite_config import SHADOW_CONFIG


class ShadowRenderer:
    """Renders drop shadows for characters with perspective and depth.

    Shadows get larger and darker as characters move toward camera (down).
    """

    def __init__(self, config: object = None) -> None:
        self.config = config or SHADOW_CONFIG
        self._shadow_cache = {}  # Cache by (width, height, depth_ratio)

    def render_character_with_shadow(
        self,
        surface: pygame.Surface,
        character_surface: pygame.Surface,
        position: Tuple[int, int],
        depth_ratio: float = 1.0,
    ) -> pygame.Rect:
        """Render a character with its drop shadow.

        Args:
            surface: Surface to draw on
            character_surface: Character sprite
            position: (x, y) position for character's feet
            depth_ratio: 0.0 (far) to 1.0 (near) for perspective scaling

        Returns:
            Rect of the drawn character (not including shadow)
        """
        if not self.config.ENABLED:
            # Just draw character without shadow
            surface.blit(character_surface, position)
            return pygame.Rect(position, character_surface.get_size())

        # Draw shadow first (underneath character)
        shadow_pos = self._draw_shadow(
            surface, character_surface, position, depth_ratio
        )

        # Draw character on top
        char_rect = character_surface.get_rect(midbottom=position)
        surface.blit(character_surface, char_rect.topleft)

        return char_rect

    def _draw_shadow(
        self,
        surface: pygame.Surface,
        character_surface: pygame.Surface,
        position: Tuple[int, int],
        depth_ratio: float,
    ) -> Tuple[int, int]:
        """Draw drop shadow at character's feet."""
        char_width, char_height = character_surface.get_size()

        # Scale shadow based on depth (larger when closer)
        scale_factor = 0.6 + depth_ratio * 0.4  # 0.6 to 1.0
        shadow_width = int(char_width * self.config.ELLIPSE_WIDTH_RATIO * scale_factor)
        shadow_height = int(self.config.ELLIPSE_HEIGHT * scale_factor)

        # Alpha increases with depth (darker when closer)
        shadow_alpha = int(self.config.BASE_ALPHA * (0.5 + depth_ratio * 0.5))

        # Get or create shadow
        shadow = self._get_shadow_surface(shadow_width, shadow_height, shadow_alpha)

        # Position shadow at character's feet with offset
        pos_x = position[0] - shadow.get_width() // 2 + self.config.OFFSET_X
        pos_y = position[1] - shadow.get_height() // 2 + self.config.OFFSET_Y

        surface.blit(shadow, (pos_x, pos_y))

        return (pos_x, pos_y)

    def _get_shadow_surface(
        self,
        width: int,
        height: int,
        alpha: int,
    ) -> pygame.Surface:
        """Get or create a shadow surface."""
        cache_key = (width, height, alpha)

        if cache_key not in self._shadow_cache:
            self._shadow_cache[cache_key] = self._create_shadow_surface(
                width, height, alpha
            )

        return self._shadow_cache[cache_key]

    def _create_shadow_surface(
        self,
        width: int,
        height: int,
        alpha: int,
    ) -> pygame.Surface:
        """Create a soft elliptical shadow."""
        # Add padding for blur
        padding = self.config.BLUR_PASSES * 2
        surface = pygame.Surface(
            (width + padding * 2, height + padding * 2),
            pygame.SRCALPHA
        )

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        # Multi-pass rendering for soft gradient
        for i in range(self.config.BLUR_PASSES, 0, -1):
            # Alpha decreases for outer layers
            layer_alpha = alpha // (self.config.BLUR_PASSES + 1 - i)
            expansion = i * 2

            rect = pygame.Rect(
                center_x - width // 2 - expansion,
                center_y - height // 2 - expansion,
                width + expansion * 2,
                height + expansion * 2,
            )

            # Draw with gradient alpha
            pygame.draw.ellipse(surface, (0, 0, 0, layer_alpha), rect)

        return surface

    def clear_cache(self) -> None:
        """Clear shadow cache (call if config changes)."""
        self._shadow_cache.clear()


# Integration helper for Character class
class CharacterShadowMixin:
    """Mixin to add shadow rendering to Character class.

    Add this to your Character class like:
        class Character(CharacterShadowMixin):
            ...
    """

    def draw_with_shadow(
        self,
        surface: pygame.Surface,
        room_height: int,
        shadow_renderer: ShadowRenderer,
    ) -> pygame.Rect:
        """Draw character with drop shadow.

        Replace the existing draw() method with this, or call from draw().
        """
        # Get current frame and position
        frame = self.current_frame
        scale = self.compute_scale(room_height)

        # Scale sprite
        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled = pygame.transform.scale(frame, (width, height))

        # Calculate depth ratio for shadow perspective
        depth_ratio = max(0.0, min(1.0, self.position.y / float(room_height)))

        # Position at character's feet
        foot_pos = (int(self.position.x), int(self.position.y))

        # Render with shadow
        return shadow_renderer.render_character_with_shadow(
            surface, scaled, foot_pos, depth_ratio
        )


# Example integration code (add to characters.py)
"""
INTEGRATION EXAMPLE - Add to zombie_quest/characters.py:

from .shadow_renderer import ShadowRenderer, CharacterShadowMixin

class Character(CharacterShadowMixin):
    # ... existing code ...

    def __init__(self, ...):
        # ... existing init ...
        self.shadow_renderer = ShadowRenderer()

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        '''Draw character with drop shadow.'''
        return self.draw_with_shadow(surface, room_height, self.shadow_renderer)
"""
