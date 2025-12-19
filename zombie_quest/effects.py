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

        # Guard against division by zero for tiny surfaces
        if max_dist < 1.0:
            max_dist = 1.0

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


# ============================================================================
# ENVIRONMENTAL EFFECTS
# ============================================================================

@dataclass
class FlutteringPoster:
    """Poster that flutters slightly from ambient air."""
    position: Tuple[int, int]
    size: Tuple[int, int]  # (width, height)
    color: Color
    flutter_speed: float = 3.0
    flutter_amount: float = 2.0  # Max pixels of flutter
    time: float = field(default=0.0)
    phase_offset: float = field(default_factory=lambda: random.uniform(0, 6.28))

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw poster with subtle flutter animation."""
        # Calculate flutter offset (sine wave with phase)
        flutter_x = math.sin(self.time * self.flutter_speed + self.phase_offset) * self.flutter_amount
        flutter_y = math.cos(self.time * self.flutter_speed * 0.7 + self.phase_offset) * self.flutter_amount * 0.5

        # Draw poster slightly offset
        pos = (int(self.position[0] + flutter_x), int(self.position[1] + flutter_y))
        pygame.draw.rect(surface, self.color, (*pos, *self.size))

        # Draw border
        pygame.draw.rect(surface, (max(0, self.color[0] - 40),
                                   max(0, self.color[1] - 40),
                                   max(0, self.color[2] - 40)),
                        (*pos, *self.size), 1)


class SmokeEmitter:
    """Emits rising smoke/steam wisps."""

    def __init__(self, position: Tuple[int, int], emit_rate: float = 0.5) -> None:
        self.position = position
        self.emit_rate = emit_rate  # Wisps per second
        self.emit_timer = 0.0
        self.wisps: List[SmokeWisp] = []

    def update(self, dt: float) -> None:
        """Update smoke emission."""
        self.emit_timer += dt

        # Emit new wisps
        while self.emit_timer >= self.emit_rate:
            self.emit_timer -= self.emit_rate
            self._emit_wisp()

        # Update wisps
        self.wisps = [w for w in self.wisps if w.update(dt)]

    def _emit_wisp(self) -> None:
        """Emit a single smoke wisp."""
        # Random horizontal offset
        offset_x = random.uniform(-5, 5)
        wisp = SmokeWisp(
            x=self.position[0] + offset_x,
            y=self.position[1],
            vx=random.uniform(-5, 5),
            vy=random.uniform(-30, -20),  # Rise upward
            life=random.uniform(2.0, 3.5),
            size=random.uniform(3, 6)
        )
        self.wisps.append(wisp)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all smoke wisps."""
        for wisp in self.wisps:
            wisp.draw(surface)


@dataclass
class SmokeWisp:
    """Individual smoke particle."""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float = field(init=False)
    size: float = 4.0

    def __post_init__(self):
        self.max_life = self.life

    def update(self, dt: float) -> bool:
        """Update wisp, return False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

        # Slow down over time
        self.vx *= 0.98
        self.vy *= 0.98

        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw smoke wisp with fade."""
        if self.life <= 0:
            return

        ratio = self.life / self.max_life
        alpha = int(50 * ratio)  # Subtle smoke
        size = int(self.size * (1.5 - ratio * 0.5))  # Expands as it rises

        # Gray smoke color
        smoke_color = (200, 190, 210)

        # Draw as circle with alpha
        smoke_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(smoke_surf, (*smoke_color, alpha), (size, size), size)
        surface.blit(smoke_surf, (int(self.x - size), int(self.y - size)))


class RedVignette:
    """Red vignette overlay for danger moments (zombie groans)."""

    def __init__(self, size: Tuple[int, int]) -> None:
        self.size = size
        self.intensity = 0.0
        self.target_intensity = 0.0
        self.fade_speed = 3.0  # How fast it fades in/out

    def trigger(self, intensity: float = 0.3, duration: float = 0.5) -> None:
        """Trigger a red vignette pulse.

        Args:
            intensity: Vignette strength (0.0-1.0)
            duration: How long to sustain before fading
        """
        self.target_intensity = intensity
        self.duration_timer = duration

    def update(self, dt: float) -> None:
        """Update vignette fade."""
        # Fade in to target
        if self.intensity < self.target_intensity:
            self.intensity = min(self.target_intensity,
                                self.intensity + self.fade_speed * dt)
        # Fade out after duration
        elif hasattr(self, 'duration_timer'):
            self.duration_timer -= dt
            if self.duration_timer <= 0:
                self.target_intensity = 0.0
                delattr(self, 'duration_timer')

        # Fade to target
        if self.intensity > self.target_intensity:
            self.intensity = max(self.target_intensity,
                               self.intensity - self.fade_speed * dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw red vignette."""
        if self.intensity <= 0:
            return

        # Create red vignette overlay
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        center_x, center_y = self.size[0] // 2, self.size[1] // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        # Guard against division by zero for tiny surfaces
        if max_dist < 1.0:
            max_dist = 1.0

        # Sample fewer points for performance
        for y in range(0, self.size[1], 4):
            for x in range(0, self.size[0], 4):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = dist / max_dist
                alpha = int(180 * self.intensity * (ratio ** 2))
                color = (255, 0, 0, alpha)
                pygame.draw.rect(overlay, color, (x, y, 4, 4))

        surface.blit(overlay, (0, 0))


class DustPuffEmitter:
    """Emits dust puffs on footsteps and direction changes."""

    def __init__(self) -> None:
        self.puffs: List[DustPuff] = []

    def emit(self, position: Tuple[float, float], direction: Optional[Tuple[float, float]] = None) -> None:
        """Emit a dust puff at position.

        Args:
            position: (x, y) where dust appears
            direction: Optional direction vector for directional puff
        """
        # Create 3-5 particles per puff
        count = random.randint(3, 5)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(10, 30)

            # If direction provided, bias particles backward
            if direction:
                dir_x, dir_y = direction
                angle = math.atan2(-dir_y, -dir_x) + random.uniform(-1, 1)
                speed = random.uniform(15, 40)

            puff = DustPuff(
                x=position[0] + random.uniform(-5, 5),
                y=position[1] + random.uniform(-3, 3),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 10,  # Slight upward
                life=random.uniform(0.3, 0.6),
                size=random.uniform(2, 4)
            )
            self.puffs.append(puff)

    def update(self, dt: float) -> None:
        """Update all dust puffs."""
        self.puffs = [p for p in self.puffs if p.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all dust puffs."""
        for puff in self.puffs:
            puff.draw(surface)


@dataclass
class DustPuff:
    """Individual dust puff particle."""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float = field(init=False)
    size: float = 3.0

    def __post_init__(self):
        self.max_life = self.life

    def update(self, dt: float) -> bool:
        """Update puff, return False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

        # Friction
        self.vx *= 0.92
        self.vy *= 0.92

        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw dust puff."""
        if self.life <= 0:
            return

        ratio = self.life / self.max_life
        alpha = int(100 * ratio)
        size = int(self.size * (1.2 - ratio * 0.2))

        # Dusty beige color
        dust_color = (200, 180, 160)

        dust_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(dust_surf, (*dust_color, alpha), (size, size), size)
        surface.blit(dust_surf, (int(self.x - size), int(self.y - size)))


class LightSpill:
    """Light spilling from doorways and exits."""

    def __init__(self, rect: pygame.Rect, color: Color, direction: str = "up") -> None:
        """
        Args:
            rect: Area where light spills
            color: Light color
            direction: "up", "down", "left", "right" - direction of spill
        """
        self.rect = rect
        self.color = color
        self.direction = direction
        self.intensity_time = 0.0
        self.pulse_speed = 1.0

    def update(self, dt: float) -> None:
        """Update light animation."""
        self.intensity_time += dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw light spill with gradient."""
        # Pulsing intensity
        pulse = (math.sin(self.intensity_time * self.pulse_speed * 2 * math.pi) + 1) / 2
        intensity = 0.3 + pulse * 0.2

        # Create gradient based on direction
        light_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        steps = 20
        if self.direction in ("up", "down"):
            for i in range(steps):
                ratio = i / steps if self.direction == "up" else 1 - i / steps
                alpha = int(80 * intensity * ratio)
                y = int(self.rect.height * i / steps)
                height = int(self.rect.height / steps) + 1
                pygame.draw.rect(light_surf, (*self.color, alpha),
                               (0, y, self.rect.width, height))
        else:  # left or right
            for i in range(steps):
                ratio = i / steps if self.direction == "left" else 1 - i / steps
                alpha = int(80 * intensity * ratio)
                x = int(self.rect.width * i / steps)
                width = int(self.rect.width / steps) + 1
                pygame.draw.rect(light_surf, (*self.color, alpha),
                               (x, 0, width, self.rect.height))

        surface.blit(light_surf, self.rect.topleft)
