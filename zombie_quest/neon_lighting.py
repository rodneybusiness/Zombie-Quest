"""Neon lighting system - makes neon signs illuminate nearby surfaces.

Uses additive blending to create authentic 1980s neon glow that affects
floors, walls, and characters near neon signs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import pygame
import math

Color = Tuple[int, int, int]
Position = Tuple[int, int]


@dataclass
class NeonLight:
    """A neon light source that emits colored glow."""
    position: Position  # (x, y) world position
    color: Color  # RGB color of neon
    intensity: float = 1.0  # 0.0 to 1.0
    radius: int = 80  # Glow radius in pixels
    flicker: bool = True  # Whether light flickers
    pulse_speed: float = 2.0  # Speed of pulsing (if any)


class NeonLightingSystem:
    """Manages neon lighting with additive blending and dynamic glow.

    Creates lighting layers that are composited onto the scene with
    additive blending for authentic neon glow.
    """

    def __init__(self, screen_size: Tuple[int, int]) -> None:
        self.screen_size = screen_size
        self.lights: List[NeonLight] = []
        self.time = 0.0

        # Create lighting layer (this gets composited additively)
        self.lighting_layer = pygame.Surface(screen_size, pygame.SRCALPHA)

        # Glow lookup table for performance
        self._glow_cache: dict = {}

    def add_light(self, light: NeonLight) -> None:
        """Add a neon light to the scene."""
        self.lights.append(light)

    def remove_light(self, light: NeonLight) -> None:
        """Remove a neon light from the scene."""
        if light in self.lights:
            self.lights.remove(light)

    def clear_lights(self) -> None:
        """Remove all lights."""
        self.lights.clear()

    def update(self, dt: float) -> None:
        """Update lighting animations (flicker, pulse)."""
        self.time += dt

    def render_lighting(self, surface: pygame.Surface) -> None:
        """Render all neon lighting effects onto the surface.

        Call this AFTER drawing the background but BEFORE drawing characters.
        """
        # Clear lighting layer
        self.lighting_layer.fill((0, 0, 0, 0))

        # Render each light
        for light in self.lights:
            self._render_light(light)

        # Composite lighting layer with additive blending
        surface.blit(self.lighting_layer, (0, 0), special_flags=pygame.BLEND_ADD)

    def _render_light(self, light: NeonLight) -> None:
        """Render a single neon light's glow."""
        # Calculate intensity with flicker/pulse
        intensity = light.intensity

        if light.flicker:
            # Realistic neon flicker
            flicker_amount = (
                math.sin(self.time * 50 + light.position[0]) * 0.1 +
                math.sin(self.time * 17 + light.position[1]) * 0.05
            )
            intensity *= (0.9 + flicker_amount)

        # Add pulse
        pulse = (math.sin(self.time * light.pulse_speed) + 1) / 2
        intensity *= (0.8 + pulse * 0.2)

        # Clamp intensity
        intensity = max(0.0, min(1.0, intensity))

        # Get or create glow surface
        glow_surface = self._get_glow_surface(light.radius, light.color, intensity)

        # Draw centered on light position
        pos = (
            light.position[0] - glow_surface.get_width() // 2,
            light.position[1] - glow_surface.get_height() // 2,
        )

        self.lighting_layer.blit(glow_surface, pos)

    def _get_glow_surface(
        self,
        radius: int,
        color: Color,
        intensity: float,
    ) -> pygame.Surface:
        """Get or create a radial glow surface."""
        # Cache key
        cache_key = (radius, color, int(intensity * 100))

        if cache_key not in self._glow_cache:
            self._glow_cache[cache_key] = self._create_glow_surface(
                radius, color, intensity
            )

        return self._glow_cache[cache_key]

    def _create_glow_surface(
        self,
        radius: int,
        color: Color,
        intensity: float,
    ) -> pygame.Surface:
        """Create a radial gradient glow surface."""
        size = radius * 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = radius

        # Draw radial gradient
        for r in range(radius, 0, -1):
            # Calculate falloff (quadratic looks best for neon)
            ratio = r / float(radius)
            falloff = 1.0 - (ratio ** 1.5)  # Quadratic falloff

            # Calculate color with intensity
            alpha = int(255 * falloff * intensity * 0.5)  # Max 50% alpha
            glow_color = (*color, alpha)

            # Draw circle
            pygame.draw.circle(surface, glow_color, (center, center), r)

        return surface

    def get_light_at_position(self, position: Position) -> Optional[Color]:
        """Get the accumulated light color at a world position.

        Useful for lighting characters based on proximity to neon.
        """
        accumulated = [0, 0, 0]

        for light in self.lights:
            # Calculate distance to light
            dx = position[0] - light.position[0]
            dy = position[1] - light.position[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < light.radius:
                # Calculate influence
                ratio = 1.0 - (distance / light.radius)
                influence = ratio ** 2  # Quadratic falloff

                # Add light contribution
                accumulated[0] += int(light.color[0] * influence * light.intensity)
                accumulated[1] += int(light.color[1] * influence * light.intensity)
                accumulated[2] += int(light.color[2] * influence * light.intensity)

        # Clamp to valid color range
        result = tuple(min(255, max(0, c)) for c in accumulated)

        if sum(result) > 0:
            return result
        return None

    def clear_cache(self) -> None:
        """Clear glow surface cache (call if lights change significantly)."""
        self._glow_cache.clear()


def create_neon_sign_lights(
    sign_text: str,
    position: Position,
    color: Color,
    char_width: int = 8,
) -> List[NeonLight]:
    """Create multiple light sources for a neon sign (one per character).

    Args:
        sign_text: Text on the sign
        position: Top-left position of sign
        color: Neon color
        char_width: Width per character

    Returns:
        List of NeonLight objects
    """
    lights = []

    for i, char in enumerate(sign_text):
        if char.strip():  # Skip spaces
            light_pos = (
                position[0] + i * char_width + char_width // 2,
                position[1] + 6,  # Center vertically
            )
            lights.append(NeonLight(
                position=light_pos,
                color=color,
                intensity=0.8,
                radius=30,
                flicker=True,
                pulse_speed=2.0 + i * 0.1,  # Slight variation
            ))

    return lights


# Integration helper for backgrounds
class NeonBackgroundMixin:
    """Mixin to add neon lighting to backgrounds.

    Add this to your background rendering system.
    """

    def setup_neon_lights(
        self,
        room_id: str,
        lighting_system: NeonLightingSystem,
    ) -> None:
        """Setup neon lights for a specific room.

        Args:
            room_id: Room identifier
            lighting_system: NeonLightingSystem instance
        """
        lighting_system.clear_lights()

        # Define neon signs per room
        if room_id == "hennepin_outside":
            # "THE NEON DEAD" marquee
            lights = create_neon_sign_lights(
                "THE NEON DEAD",
                position=(178, 46),
                color=(255, 100, 200),
                char_width=7,
            )
            for light in lights:
                lighting_system.add_light(light)

            # "OPEN" sign at record store
            lights = create_neon_sign_lights(
                "OPEN",
                position=(65, 45),
                color=(100, 255, 150),
                char_width=10,
            )
            for light in lights:
                lighting_system.add_light(light)

            # Street lights
            for x in [82, 202, 292]:
                lighting_system.add_light(NeonLight(
                    position=(x, 55),
                    color=(255, 240, 200),
                    intensity=0.6,
                    radius=60,
                    flicker=False,
                    pulse_speed=0.5,
                ))

        elif room_id == "record_store":
            # "VINYL" neon sign
            lights = create_neon_sign_lights(
                "VINYL",
                position=(140, 35),
                color=(255, 100, 200),
                char_width=12,
            )
            for light in lights:
                lighting_system.add_light(light)

        elif room_id == "college_station":
            # "ON AIR" light
            lighting_system.add_light(NeonLight(
                position=(170, 52),
                color=(255, 50, 50),
                intensity=1.0,
                radius=50,
                flicker=True,
                pulse_speed=5.0,
            ))

        elif room_id == "backstage_stage":
            # Makeup mirror lights
            for x in [52, 112]:
                for y in range(40, 85, 10):
                    lighting_system.add_light(NeonLight(
                        position=(x, y),
                        color=(255, 240, 200),
                        intensity=0.7,
                        radius=25,
                        flicker=False,
                    ))


"""
INTEGRATION EXAMPLE - Add to zombie_quest/ui.py or engine.py:

from .neon_lighting import NeonLightingSystem, NeonBackgroundMixin

class GameRenderer(NeonBackgroundMixin):
    def __init__(self, screen_size):
        self.neon_lighting = NeonLightingSystem(screen_size)
        # ... rest of init

    def render_room(self, surface, room_id, background):
        # 1. Draw background
        surface.blit(background, (0, 0))

        # 2. Setup and render neon lights
        self.setup_neon_lights(room_id, self.neon_lighting)
        self.neon_lighting.update(dt)  # Pass delta time
        self.neon_lighting.render_lighting(surface)

        # 3. Draw characters (they'll be lit by neon)
        # ... draw characters ...

        # 4. Draw foreground elements
        # ... draw foreground ...
"""
