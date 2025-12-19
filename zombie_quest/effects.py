"""Visual effects system - particles, glow, transitions, screen effects."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pygame

from .config import ANIMATION, COLORS

Color = Tuple[int, int, int]


@dataclass
class Particle:
    """Individual particle for effects."""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Color
    size: float
    gravity: float = 0.0
    fade: bool = True
    shrink: bool = True

    def update(self, dt: float) -> bool:
        """Update particle, return False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the particle."""
        if self.life <= 0:
            return

        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 255
        size = max(1, int(self.size * ratio)) if self.shrink else int(self.size)

        # Create particle surface with alpha
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)

        surface.blit(particle_surf, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    """Manages multiple particle effects."""

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def update(self, dt: float) -> None:
        """Update all particles."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)

    def emit_burst(self, x: float, y: float, color: Color, count: int = 10,
                   speed: float = 50.0, lifetime: float = 1.0) -> None:
        """Emit a burst of particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed_var = random.uniform(0.5, 1.5) * speed
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed_var,
                vy=math.sin(angle) * speed_var,
                life=lifetime * random.uniform(0.5, 1.0),
                max_life=lifetime,
                color=color,
                size=random.uniform(2, 5),
                gravity=20.0
            ))

    def emit_sparkle(self, x: float, y: float, color: Color) -> None:
        """Emit a sparkle effect (item pickup)."""
        for i in range(8):
            angle = i * (math.pi / 4)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * 40,
                vy=math.sin(angle) * 40 - 20,
                life=0.5,
                max_life=0.5,
                color=color,
                size=3,
                gravity=-10
            ))

    def emit_damage(self, x: float, y: float) -> None:
        """Emit damage particles (red flash)."""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            self.particles.append(Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-20, 0),
                vx=math.cos(angle) * random.uniform(20, 60),
                vy=math.sin(angle) * random.uniform(20, 60) - 30,
                life=0.4,
                max_life=0.4,
                color=(255, 50, 50),
                size=random.uniform(2, 4),
                gravity=100
            ))

    def emit_ambient_dust(self, bounds: pygame.Rect) -> None:
        """Emit ambient floating dust particles."""
        if random.random() > 0.1:  # 10% chance per call
            return
        self.particles.append(Particle(
            x=random.uniform(bounds.left, bounds.right),
            y=bounds.bottom,
            vx=random.uniform(-5, 5),
            vy=random.uniform(-15, -5),
            life=3.0,
            max_life=3.0,
            color=(200, 180, 220),
            size=1,
            gravity=-2,
            fade=True,
            shrink=False
        ))


class ScreenTransition:
    """Screen transition effects."""

    def __init__(self) -> None:
        self.active = False
        self.progress = 0.0
        self.duration = ANIMATION.TRANSITION_DURATION
        self.fade_in = True  # True = fading in, False = fading out
        self.callback: Optional[callable] = None
        self.halfway_callback: Optional[callable] = None
        self.halfway_called = False

    def start_transition(self, callback: Optional[callable] = None,
                        halfway_callback: Optional[callable] = None) -> None:
        """Start a fade out -> action -> fade in transition."""
        self.active = True
        self.progress = 0.0
        self.fade_in = False  # Start by fading out
        self.callback = callback
        self.halfway_callback = halfway_callback
        self.halfway_called = False

    def update(self, dt: float) -> bool:
        """Update transition, return True if still active."""
        if not self.active:
            return False

        self.progress += dt / self.duration

        if self.progress >= 1.0:
            if not self.fade_in:
                # Finished fading out, call halfway callback and fade in
                if self.halfway_callback and not self.halfway_called:
                    self.halfway_callback()
                    self.halfway_called = True
                self.fade_in = True
                self.progress = 0.0
            else:
                # Finished fading in
                self.active = False
                if self.callback:
                    self.callback()
                return False

        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the transition overlay."""
        if not self.active:
            return

        if self.fade_in:
            alpha = int(255 * (1.0 - self.progress))
        else:
            alpha = int(255 * self.progress)

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))


class GlowEffect:
    """Creates pulsing glow effects for neon elements."""

    def __init__(self) -> None:
        self.time = 0.0

    def update(self, dt: float) -> None:
        """Update glow animation."""
        self.time += dt

    def get_glow_intensity(self, speed: float = 1.0, min_val: float = 0.6) -> float:
        """Get current glow intensity (0-1)."""
        pulse = (math.sin(self.time * ANIMATION.GLOW_PULSE_SPEED * speed) + 1) / 2
        return min_val + pulse * (1.0 - min_val)

    def apply_glow(self, surface: pygame.Surface, color: Color, intensity: float = 1.0) -> pygame.Surface:
        """Apply glow effect to a surface."""
        glow_amount = self.get_glow_intensity() * intensity

        # Create glow surface
        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Draw multiple expanding layers
        for i in range(3):
            layer_alpha = int(50 * glow_amount * (1 - i/3))
            expand = (i + 1) * 2
            scaled_size = (surface.get_width() + expand * 2, surface.get_height() + expand * 2)
            scaled = pygame.transform.scale(surface, scaled_size)

            # Tint the scaled surface
            tinted = pygame.Surface(scaled_size, pygame.SRCALPHA)
            tinted.fill((*color, layer_alpha))
            scaled.blit(tinted, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            glow.blit(scaled, (-expand, -expand))

        # Composite original on top
        result = glow.copy()
        result.blit(surface, (0, 0))

        return result

    def draw_glow_rect(self, surface: pygame.Surface, rect: pygame.Rect,
                       color: Color, width: int = 2) -> None:
        """Draw a glowing rectangle."""
        intensity = self.get_glow_intensity()

        # Draw multiple glow layers
        for i in range(4):
            alpha = int(100 * intensity * (1 - i/4))
            expanded = rect.inflate(i * 4, i * 4)
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, alpha), expanded, width + i)
            surface.blit(glow_surf, (0, 0))

        # Draw core rect
        pygame.draw.rect(surface, color, rect, width)


class ScreenShake:
    """Screen shake effect for impact moments."""

    def __init__(self) -> None:
        self.intensity = 0.0
        self.duration = 0.0
        self.time = 0.0

    def shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger a screen shake."""
        self.intensity = intensity
        self.duration = duration
        self.time = 0.0

    def update(self, dt: float) -> Tuple[int, int]:
        """Update and return offset to apply."""
        if self.time >= self.duration:
            return (0, 0)

        self.time += dt
        remaining = 1.0 - (self.time / self.duration)
        current_intensity = self.intensity * remaining

        offset_x = int(random.uniform(-current_intensity, current_intensity))
        offset_y = int(random.uniform(-current_intensity, current_intensity))

        return (offset_x, offset_y)


class ScanlineOverlay:
    """CRT scanline effect for retro feel."""

    def __init__(self, size: Tuple[int, int], intensity: float = 0.15) -> None:
        self.overlay = pygame.Surface(size, pygame.SRCALPHA)

        for y in range(0, size[1], 2):
            pygame.draw.line(self.overlay, (0, 0, 0, int(255 * intensity)),
                           (0, y), (size[0], y))

    def draw(self, surface: pygame.Surface) -> None:
        """Apply scanline overlay."""
        surface.blit(self.overlay, (0, 0))


class VignetteOverlay:
    """Vignette effect for atmospheric edges."""

    def __init__(self, size: Tuple[int, int], intensity: float = 0.4) -> None:
        self.overlay = pygame.Surface(size, pygame.SRCALPHA)
        center_x, center_y = size[0] // 2, size[1] // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        for y in range(size[1]):
            for x in range(size[0]):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = dist / max_dist
                alpha = int(255 * intensity * (ratio ** 2))
                self.overlay.set_at((x, y), (0, 0, 0, alpha))

    def draw(self, surface: pygame.Surface) -> None:
        """Apply vignette overlay."""
        surface.blit(self.overlay, (0, 0))


@dataclass
class FlickerLight:
    """Flickering light effect for neon signs."""
    position: Tuple[int, int]
    color: Color
    radius: int
    flicker_speed: float = 5.0
    min_intensity: float = 0.7
    time: float = field(default=0.0)

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface) -> None:
        intensity = self.min_intensity + (1 - self.min_intensity) * \
                    (0.5 + 0.5 * math.sin(self.time * self.flicker_speed +
                     math.sin(self.time * 7) * 0.5))

        # Random flicker
        if random.random() < 0.02:
            intensity *= 0.3

        # Draw glow layers
        for i in range(3):
            layer_radius = self.radius + i * 4
            alpha = int(60 * intensity * (1 - i/3))
            glow_surf = pygame.Surface((layer_radius*2, layer_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha),
                             (layer_radius, layer_radius), layer_radius)
            surface.blit(glow_surf,
                        (self.position[0] - layer_radius, self.position[1] - layer_radius))
