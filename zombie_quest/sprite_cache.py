"""Sprite caching system - prevents expensive regeneration every frame.

Generates sprites once, caches them intelligently, and provides fast lookup.
Includes shadow generation, 8-direction support, and idle animations.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import pygame

from .sprite_config import (
    SHADOW_CONFIG,
    DIAGONAL_CONFIG,
    IDLE_CONFIG,
)

Direction = str
CacheKey = Tuple[str, Direction, int, float]  # (char_type, direction, frame, scale)


class SpriteCache:
    """Global sprite cache to prevent regeneration.

    Usage:
        cache = SpriteCache()
        sprite = cache.get_hero_sprite(direction="down", frame=0, scale=2.5)
        shadow = cache.get_character_shadow(sprite)
    """

    def __init__(self) -> None:
        self._sprite_cache: Dict[CacheKey, pygame.Surface] = {}
        self._shadow_cache: Dict[Tuple[int, int], pygame.Surface] = {}  # (width, height)
        self._animation_sets: Dict[str, Dict[Direction, List[pygame.Surface]]] = {}

    def clear(self) -> None:
        """Clear all caches (for memory management or sprite updates)."""
        self._sprite_cache.clear()
        self._shadow_cache.clear()
        self._animation_sets.clear()

    def get_sprite(
        self,
        char_type: str,
        direction: Direction,
        frame: int,
        scale: float,
        generator_func: callable,
    ) -> pygame.Surface:
        """Get or generate a sprite.

        Args:
            char_type: "hero", "zombie_scene", etc.
            direction: "up", "down", "left", "right", or diagonal
            frame: Animation frame number
            scale: Scale multiplier
            generator_func: Function to generate sprite if not cached

        Returns:
            Cached or newly generated sprite surface
        """
        key = (char_type, direction, frame, scale)

        if key not in self._sprite_cache:
            # Generate and cache
            sprite = generator_func(direction, frame, scale)
            self._sprite_cache[key] = sprite

        return self._sprite_cache[key]

    def get_animation_set(
        self,
        char_type: str,
        generator_func: callable,
        **kwargs
    ) -> Dict[Direction, List[pygame.Surface]]:
        """Get complete animation set for a character.

        Args:
            char_type: Unique identifier like "hero" or "zombie_bouncer"
            generator_func: Function that generates all animations
            **kwargs: Arguments to pass to generator

        Returns:
            Dictionary mapping directions to frame lists
        """
        if char_type not in self._animation_sets:
            self._animation_sets[char_type] = generator_func(**kwargs)

        return self._animation_sets[char_type]

    def get_character_shadow(
        self,
        character_surface: pygame.Surface,
        config: Optional[object] = None,
    ) -> pygame.Surface:
        """Generate or retrieve drop shadow for a character.

        Args:
            character_surface: The character sprite to create shadow for
            config: Shadow configuration (uses SHADOW_CONFIG if None)

        Returns:
            Shadow surface with alpha channel
        """
        if config is None:
            config = SHADOW_CONFIG

        if not config.ENABLED:
            # Return empty surface
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        size_key = character_surface.get_size()

        if size_key not in self._shadow_cache:
            self._shadow_cache[size_key] = self._generate_shadow(
                character_surface, config
            )

        return self._shadow_cache[size_key]

    def _generate_shadow(
        self,
        character_surface: pygame.Surface,
        config: object,
    ) -> pygame.Surface:
        """Generate a drop shadow surface."""
        char_width, char_height = character_surface.get_size()

        # Shadow is an ellipse at the character's feet
        shadow_width = int(char_width * config.ELLIPSE_WIDTH_RATIO)
        shadow_height = config.ELLIPSE_HEIGHT

        # Create shadow surface with extra space for blur
        padding = config.BLUR_PASSES * 2
        shadow_surface = pygame.Surface(
            (shadow_width + padding * 2, shadow_height + padding * 2),
            pygame.SRCALPHA
        )

        # Draw ellipse shadow
        center_x = shadow_surface.get_width() // 2
        center_y = shadow_surface.get_height() // 2

        # Multi-pass for soft shadow
        for i in range(config.BLUR_PASSES, 0, -1):
            alpha = config.BASE_ALPHA // (config.BLUR_PASSES + 1 - i)
            expansion = i * 2
            rect = pygame.Rect(
                center_x - (shadow_width // 2) - expansion,
                center_y - (shadow_height // 2) - expansion,
                shadow_width + expansion * 2,
                shadow_height + expansion * 2,
            )
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, alpha), rect)

        return shadow_surface

    def preload_character(
        self,
        char_type: str,
        directions: List[Direction],
        frame_count: int,
        scale: float,
        generator_func: callable,
    ) -> None:
        """Preload all sprites for a character to avoid runtime generation.

        Call this during loading screens or initialization.
        """
        for direction in directions:
            for frame in range(frame_count):
                self.get_sprite(char_type, direction, frame, scale, generator_func)

    def get_memory_usage(self) -> Dict[str, int]:
        """Get cache memory usage statistics."""
        sprite_count = len(self._sprite_cache)
        shadow_count = len(self._shadow_cache)
        animation_count = len(self._animation_sets)

        # Estimate memory (rough approximation)
        sprite_bytes = sum(
            s.get_width() * s.get_height() * 4  # RGBA
            for s in self._sprite_cache.values()
        )
        shadow_bytes = sum(
            s.get_width() * s.get_height() * 4
            for s in self._shadow_cache.values()
        )

        return {
            "sprite_count": sprite_count,
            "shadow_count": shadow_count,
            "animation_sets": animation_count,
            "sprite_bytes": sprite_bytes,
            "shadow_bytes": shadow_bytes,
            "total_bytes": sprite_bytes + shadow_bytes,
        }


# Global cache instance
_global_cache: Optional[SpriteCache] = None


def get_global_cache() -> SpriteCache:
    """Get or create the global sprite cache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = SpriteCache()
    return _global_cache


def clear_global_cache() -> None:
    """Clear the global sprite cache."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()
