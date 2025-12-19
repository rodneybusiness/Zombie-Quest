"""Enhanced CRT shader - authentic 1980s monitor effects.

Implements:
- Scanlines with proper intensity
- Screen curvature (barrel distortion)
- Chromatic aberration (RGB separation)
- Phosphor glow and bloom
- Vignette darkening at edges
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import pygame
import math
import numpy as np

Color = Tuple[int, int, int]


@dataclass
class CRTConfig:
    """Configuration for CRT shader effects."""
    # Scanlines
    scanline_intensity: float = 0.15  # 0.0 to 1.0
    scanline_thickness: int = 2  # Pixels between scanlines

    # Curvature
    curvature_enabled: bool = True
    curvature_amount: float = 0.15  # 0.0 to 1.0 (barrel distortion)

    # Chromatic aberration
    chromatic_aberration: bool = True
    aberration_amount: float = 1.5  # Pixels of RGB separation

    # Phosphor glow
    phosphor_glow: bool = True
    glow_intensity: float = 0.3  # 0.0 to 1.0
    glow_radius: int = 2  # Blur radius for glow

    # Vignette
    vignette_enabled: bool = True
    vignette_intensity: float = 0.4  # 0.0 to 1.0

    # Noise/grain
    noise_enabled: bool = True
    noise_intensity: float = 0.05  # 0.0 to 1.0


class CRTShader:
    """Applies CRT monitor effects to the game screen.

    This creates an authentic 1980s CRT television/monitor look.
    """

    def __init__(self, screen_size: Tuple[int, int], config: CRTConfig = None) -> None:
        self.screen_size = screen_size
        self.config = config or CRTConfig()

        # Pre-generate static overlays
        self.scanline_overlay = self._create_scanline_overlay()
        self.vignette_overlay = self._create_vignette_overlay()

        # Curvature mapping (for performance)
        self.curvature_map = None
        if self.config.curvature_enabled:
            self.curvature_map = self._create_curvature_map()

        # Frame counter for noise animation
        self.frame = 0

    def apply_crt_effect(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply all CRT effects to a surface.

        Args:
            surface: Input surface to process

        Returns:
            New surface with CRT effects applied
        """
        self.frame += 1

        # Start with original surface
        result = surface.copy()

        # 1. Apply chromatic aberration
        if self.config.chromatic_aberration:
            result = self._apply_chromatic_aberration(result)

        # 2. Apply curvature (barrel distortion)
        if self.config.curvature_enabled and self.curvature_map is not None:
            result = self._apply_curvature(result)

        # 3. Apply phosphor glow
        if self.config.phosphor_glow:
            result = self._apply_phosphor_glow(result)

        # 4. Apply scanlines
        result.blit(self.scanline_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

        # 5. Apply vignette
        if self.config.vignette_enabled:
            result.blit(self.vignette_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

        # 6. Apply noise/grain
        if self.config.noise_enabled:
            result = self._apply_noise(result)

        return result

    def _create_scanline_overlay(self) -> pygame.Surface:
        """Create scanline overlay (horizontal lines)."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 255))

        width, height = self.screen_size
        darkness = int(255 * self.config.scanline_intensity)

        for y in range(0, height, self.config.scanline_thickness):
            pygame.draw.line(
                overlay,
                (255 - darkness, 255 - darkness, 255 - darkness, 255),
                (0, y),
                (width, y),
                1
            )

        return overlay

    def _create_vignette_overlay(self) -> pygame.Surface:
        """Create vignette overlay (darkens edges)."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        width, height = self.screen_size
        center_x, center_y = width // 2, height // 2

        # Calculate max distance from center
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        # Draw radial gradient
        for y in range(height):
            for x in range(width):
                # Distance from center
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx * dx + dy * dy)

                # Vignette falloff (quadratic)
                ratio = dist / max_dist
                darkness = int(255 * self.config.vignette_intensity * (ratio ** 2))

                # Darker at edges
                color_val = 255 - darkness
                overlay.set_at((x, y), (color_val, color_val, color_val, 255))

        return overlay

    def _create_curvature_map(self) -> dict:
        """Create lookup table for barrel distortion.

        Maps each output pixel to its source pixel in the flat image.
        """
        width, height = self.screen_size
        mapping = {}

        center_x, center_y = width / 2.0, height / 2.0

        for y in range(height):
            for x in range(width):
                # Normalize coordinates to -1 to 1
                nx = (x - center_x) / center_x
                ny = (y - center_y) / center_y

                # Apply barrel distortion
                r2 = nx * nx + ny * ny
                distortion = 1.0 + self.config.curvature_amount * r2

                # Calculate source coordinates
                src_x = center_x + nx * center_x / distortion
                src_y = center_y + ny * center_y / distortion

                # Clamp to valid range
                src_x = max(0, min(width - 1, src_x))
                src_y = max(0, min(height - 1, src_y))

                mapping[(x, y)] = (int(src_x), int(src_y))

        return mapping

    def _apply_curvature(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply barrel distortion to simulate curved CRT screen."""
        result = pygame.Surface(self.screen_size)
        result.fill((0, 0, 0))  # Black background for curved edges

        width, height = self.screen_size

        # Use curvature map for fast lookup
        for y in range(height):
            for x in range(width):
                src_x, src_y = self.curvature_map[(x, y)]
                try:
                    color = surface.get_at((src_x, src_y))
                    result.set_at((x, y), color)
                except IndexError:
                    pass  # Outside bounds, keep black

        return result

    def _apply_chromatic_aberration(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply RGB channel separation (chromatic aberration)."""
        width, height = self.screen_size
        result = pygame.Surface(self.screen_size)

        offset = int(self.config.aberration_amount)

        # Extract RGB channels as separate surfaces
        red_channel = pygame.Surface(self.screen_size)
        green_channel = pygame.Surface(self.screen_size)
        blue_channel = pygame.Surface(self.screen_size)

        # Copy with offsets
        for y in range(height):
            for x in range(width):
                color = surface.get_at((x, y))

                # Red channel - shift left
                if x >= offset:
                    red_channel.set_at((x - offset, y), (color[0], 0, 0))

                # Green channel - no shift
                green_channel.set_at((x, y), (0, color[1], 0))

                # Blue channel - shift right
                if x < width - offset:
                    blue_channel.set_at((x + offset, y), (0, 0, color[2]))

        # Combine channels
        result.fill((0, 0, 0))
        result.blit(red_channel, (0, 0), special_flags=pygame.BLEND_ADD)
        result.blit(green_channel, (0, 0), special_flags=pygame.BLEND_ADD)
        result.blit(blue_channel, (0, 0), special_flags=pygame.BLEND_ADD)

        return result

    def _apply_phosphor_glow(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply phosphor glow effect (bright areas bloom)."""
        # Create glow layer
        glow = surface.copy()

        # Brighten only bright pixels
        width, height = self.screen_size
        threshold = 180  # Only glow bright pixels

        for y in range(height):
            for x in range(width):
                color = glow.get_at((x, y))
                brightness = (color[0] + color[1] + color[2]) / 3

                if brightness < threshold:
                    glow.set_at((x, y), (0, 0, 0, 0))
                else:
                    # Amplify bright pixels
                    factor = 1.5
                    new_color = (
                        min(255, int(color[0] * factor)),
                        min(255, int(color[1] * factor)),
                        min(255, int(color[2] * factor)),
                    )
                    glow.set_at((x, y), new_color)

        # Simple box blur for glow
        glow = self._box_blur(glow, self.config.glow_radius)

        # Composite glow with original
        glow.set_alpha(int(255 * self.config.glow_intensity))
        result = surface.copy()
        result.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        return result

    def _box_blur(self, surface: pygame.Surface, radius: int) -> pygame.Surface:
        """Simple box blur for glow effect."""
        # This is a simplified blur - in production, use pygame's transform
        # or implement a proper Gaussian blur
        result = surface.copy()
        width, height = surface.get_size()

        for y in range(height):
            for x in range(width):
                # Sample surrounding pixels
                colors = []
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        sx, sy = x + dx, y + dy
                        if 0 <= sx < width and 0 <= sy < height:
                            colors.append(surface.get_at((sx, sy)))

                if colors:
                    # Average color
                    avg_r = sum(c[0] for c in colors) // len(colors)
                    avg_g = sum(c[1] for c in colors) // len(colors)
                    avg_b = sum(c[2] for c in colors) // len(colors)
                    result.set_at((x, y), (avg_r, avg_g, avg_b))

        return result

    def _apply_noise(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply scanline noise/grain."""
        result = surface.copy()
        width, height = self.screen_size

        # Animated noise using frame counter
        import random
        random.seed(self.frame)

        noise_amount = int(255 * self.config.noise_intensity)

        # Add noise to random pixels
        noise_pixels = int(width * height * 0.02)  # 2% of pixels
        for _ in range(noise_pixels):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            color = result.get_at((x, y))
            noise = random.randint(-noise_amount, noise_amount)

            new_color = (
                max(0, min(255, color[0] + noise)),
                max(0, min(255, color[1] + noise)),
                max(0, min(255, color[2] + noise)),
            )
            result.set_at((x, y), new_color)

        return result


"""
INTEGRATION EXAMPLE - Add to zombie_quest/ui.py or main rendering loop:

from .crt_shader import CRTShader, CRTConfig

class GameRenderer:
    def __init__(self, screen_size):
        # Create CRT shader with custom config
        crt_config = CRTConfig(
            scanline_intensity=0.15,
            curvature_enabled=True,
            curvature_amount=0.12,
            chromatic_aberration=True,
            aberration_amount=1.0,
            phosphor_glow=True,
            glow_intensity=0.25,
        )
        self.crt_shader = CRTShader(screen_size, crt_config)

    def render_final_frame(self, game_surface):
        '''Apply CRT effect to final rendered frame.'''
        # Apply CRT shader
        crt_surface = self.crt_shader.apply_crt_effect(game_surface)

        # Display to screen
        self.screen.blit(crt_surface, (0, 0))
        pygame.display.flip()

# Or in main game loop:
def main():
    screen = pygame.display.set_mode((640, 480))
    game_surface = pygame.Surface((320, 240))  # Render at lower res
    crt = CRTShader((320, 240))

    while running:
        # Render game to game_surface
        # ... render everything ...

        # Apply CRT effect
        final = crt.apply_crt_effect(game_surface)

        # Scale up and display
        scaled = pygame.transform.scale(final, (640, 480))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
"""
