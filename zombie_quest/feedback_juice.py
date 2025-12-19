"""Screen effects for maximum game feel juice.

Features:
- Item pickup: zoom pulse effect
- Damage taken: red vignette flash
- Room transition: cinematic letterbox
- Success moments: sparkle burst
- UI interactions: micro-animations
- Freeze frames for impact
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

from .config import COLORS, ANIMATION

Color = Tuple[int, int, int]


@dataclass
class ZoomPulse:
    """Quick zoom pulse effect for item pickups."""

    def __init__(self) -> None:
        self.active = False
        self.time = 0.0
        self.duration = 0.25  # Quick pulse
        self.intensity = 0.05  # 5% zoom

    def trigger(self) -> None:
        """Start the pulse effect."""
        self.active = True
        self.time = 0.0

    def update(self, dt: float) -> float:
        """Update and return current zoom scale."""
        if not self.active:
            return 1.0

        self.time += dt

        if self.time >= self.duration:
            self.active = False
            return 1.0

        # Ease out elastic
        progress = self.time / self.duration
        zoom = 1.0 + self.intensity * (1.0 - progress) * math.sin(progress * math.pi * 4)

        return zoom

    def is_active(self) -> bool:
        """Check if pulse is active."""
        return self.active


class DamageVignette:
    """Red vignette flash for damage feedback."""

    def __init__(self) -> None:
        self.active = False
        self.intensity = 0.0
        self.max_intensity = 0.6
        self.fade_speed = 2.5

    def trigger(self, intensity: float = 0.6) -> None:
        """Trigger damage flash."""
        self.active = True
        self.intensity = min(1.0, intensity)
        self.max_intensity = self.intensity

    def update(self, dt: float) -> None:
        """Update vignette fade."""
        if self.active:
            self.intensity -= self.fade_speed * dt
            if self.intensity <= 0:
                self.intensity = 0
                self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw damage vignette."""
        if not self.active or self.intensity <= 0:
            return

        width, height = surface.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create radial gradient from edges
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        # Sample points for performance
        step = 4
        for y in range(0, height, step):
            for x in range(0, width, step):
                # Distance from center
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx * dx + dy * dy)

                # Normalized distance (1.0 at edges, 0.0 at center)
                norm_dist = min(1.0, dist / max_dist)

                # Vignette strength increases toward edges
                alpha = int(self.intensity * 255 * (norm_dist ** 1.5))

                if alpha > 0:
                    pygame.draw.rect(vignette, (255, 0, 0, alpha),
                                   (x, y, step, step))

        surface.blit(vignette, (0, 0))


class CinematicLetterbox:
    """Cinematic letterbox bars for room transitions."""

    def __init__(self) -> None:
        self.active = False
        self.bar_height = 0
        self.target_height = 40
        self.animation_speed = 200  # Pixels per second

    def show(self) -> None:
        """Show letterbox bars."""
        self.active = True

    def hide(self) -> None:
        """Hide letterbox bars."""
        self.active = False

    def update(self, dt: float) -> None:
        """Update letterbox animation."""
        if self.active:
            # Slide in
            if self.bar_height < self.target_height:
                self.bar_height = min(self.target_height,
                                     self.bar_height + self.animation_speed * dt)
        else:
            # Slide out
            if self.bar_height > 0:
                self.bar_height = max(0, self.bar_height - self.animation_speed * dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw letterbox bars."""
        if self.bar_height <= 0:
            return

        width, height = surface.get_size()
        bar_height = int(self.bar_height)

        # Top bar
        top_bar = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        top_bar.fill((0, 0, 0, 255))
        surface.blit(top_bar, (0, 0))

        # Bottom bar
        bottom_bar = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        bottom_bar.fill((0, 0, 0, 255))
        surface.blit(bottom_bar, (0, height - bar_height))

        # Subtle gradient on bars
        for i in range(bar_height):
            alpha = int(100 * (1 - i / bar_height))
            # Top gradient (downward)
            pygame.draw.line(surface, (*COLORS.DEEP_PURPLE, alpha),
                           (0, bar_height - i), (width, bar_height - i))
            # Bottom gradient (upward)
            pygame.draw.line(surface, (*COLORS.DEEP_PURPLE, alpha),
                           (0, height - bar_height + i), (width, height - bar_height + i))

    def is_visible(self) -> bool:
        """Check if letterbox is visible."""
        return self.bar_height > 0


class SuccessFlash:
    """Bright flash for successful actions."""

    def __init__(self) -> None:
        self.active = False
        self.intensity = 0.0
        self.color: Color = COLORS.NEON_GOLD
        self.duration = 0.2
        self.time = 0.0

    def trigger(self, color: Optional[Color] = None) -> None:
        """Trigger success flash."""
        self.active = True
        self.intensity = 1.0
        self.time = 0.0
        if color:
            self.color = color

    def update(self, dt: float) -> None:
        """Update flash."""
        if self.active:
            self.time += dt
            progress = min(1.0, self.time / self.duration)

            # Ease out
            self.intensity = 1.0 - (progress ** 2)

            if progress >= 1.0:
                self.active = False
                self.intensity = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw success flash."""
        if not self.active or self.intensity <= 0:
            return

        flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(self.intensity * 120)
        flash.fill((*self.color, alpha))
        surface.blit(flash, (0, 0))


class FreezeFrame:
    """Brief pause in action for impact moments."""

    def __init__(self) -> None:
        self.active = False
        self.duration = 0.0
        self.time = 0.0

    def trigger(self, duration: float = 0.08) -> None:
        """Trigger a freeze frame."""
        self.active = True
        self.duration = duration
        self.time = 0.0

    def update(self, dt: float) -> float:
        """Update freeze frame. Returns actual dt to use (0 if frozen)."""
        if not self.active:
            return dt

        self.time += dt

        if self.time >= self.duration:
            self.active = False
            # Return remaining time
            return self.time - self.duration

        # Frozen - return 0 dt
        return 0.0

    def is_active(self) -> bool:
        """Check if freeze is active."""
        return self.active


class ChromaticAberration:
    """RGB split effect for intense moments."""

    def __init__(self) -> None:
        self.intensity = 0.0
        self.target_intensity = 0.0
        self.fade_speed = 5.0

    def trigger(self, intensity: float = 0.5) -> None:
        """Trigger chromatic aberration."""
        self.target_intensity = intensity

    def update(self, dt: float) -> None:
        """Update effect intensity."""
        if self.intensity < self.target_intensity:
            self.intensity = min(self.target_intensity,
                               self.intensity + self.fade_speed * dt)
        elif self.intensity > self.target_intensity:
            self.intensity = max(self.target_intensity,
                               self.intensity - self.fade_speed * dt)

        # Auto-fade to zero
        if self.target_intensity > 0:
            self.target_intensity = max(0, self.target_intensity - self.fade_speed * dt * 0.5)

    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply chromatic aberration to surface."""
        if self.intensity <= 0.01:
            return surface

        width, height = surface.get_size()
        result = pygame.Surface((width, height), pygame.SRCALPHA)

        # Offset amount
        offset = int(self.intensity * 3)

        # Get RGB channels
        r_surf = surface.copy()
        g_surf = surface.copy()
        b_surf = surface.copy()

        # Create channel masks
        r_mask = pygame.Surface((width, height), pygame.SRCALPHA)
        r_mask.fill((255, 0, 0, 255))
        r_surf.blit(r_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        g_mask = pygame.Surface((width, height), pygame.SRCALPHA)
        g_mask.fill((0, 255, 0, 255))
        g_surf.blit(g_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        b_mask = pygame.Surface((width, height), pygame.SRCALPHA)
        b_mask.fill((0, 0, 255, 255))
        b_surf.blit(b_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Offset and composite
        result.blit(r_surf, (-offset, 0))
        result.blit(g_surf, (0, 0))
        result.blit(b_surf, (offset, 0))

        return result


class FeedbackJuice:
    """Master controller for all feedback effects."""

    def __init__(self) -> None:
        self.zoom_pulse = ZoomPulse()
        self.damage_vignette = DamageVignette()
        self.letterbox = CinematicLetterbox()
        self.success_flash = SuccessFlash()
        self.freeze_frame = FreezeFrame()
        self.chromatic = ChromaticAberration()

    def item_pickup(self) -> None:
        """Trigger item pickup feedback."""
        self.zoom_pulse.trigger()
        self.success_flash.trigger(COLORS.NEON_GOLD)

    def damage_taken(self, intensity: float = 0.6) -> None:
        """Trigger damage feedback."""
        self.damage_vignette.trigger(intensity)
        self.freeze_frame.trigger(0.08)
        self.chromatic.trigger(0.4)

    def room_transition_start(self) -> None:
        """Start room transition."""
        self.letterbox.show()

    def room_transition_end(self) -> None:
        """End room transition."""
        self.letterbox.hide()

    def success_moment(self, color: Optional[Color] = None) -> None:
        """Trigger success feedback."""
        self.success_flash.trigger(color or COLORS.CYAN_GLOW)

    def impact_hit(self) -> None:
        """Heavy impact feedback."""
        self.freeze_frame.trigger(0.12)
        self.chromatic.trigger(0.6)

    def update(self, dt: float) -> float:
        """Update all effects. Returns modified dt (for freeze frames)."""
        # Freeze frame modifies dt
        actual_dt = self.freeze_frame.update(dt)

        # Other effects update normally
        self.zoom_pulse.update(actual_dt)
        self.damage_vignette.update(actual_dt)
        self.letterbox.update(actual_dt)
        self.success_flash.update(actual_dt)
        self.chromatic.update(actual_dt)

        return actual_dt

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all screen effects."""
        # Draw effects that overlay the entire screen
        self.damage_vignette.draw(surface)
        self.success_flash.draw(surface)
        self.letterbox.draw(surface)

    def get_zoom_scale(self) -> float:
        """Get current zoom scale for camera."""
        return self.zoom_pulse.update(0)

    def should_freeze(self) -> bool:
        """Check if game should be frozen."""
        return self.freeze_frame.is_active()


class UIFeedback:
    """Micro-animations for UI interactions."""

    def __init__(self) -> None:
        self.button_scales: dict[str, float] = {}
        self.button_scale_targets: dict[str, float] = {}
        self.scale_speed = 10.0

    def button_press(self, button_id: str) -> None:
        """Trigger button press animation."""
        self.button_scale_targets[button_id] = 0.95

    def button_release(self, button_id: str) -> None:
        """Trigger button release animation."""
        self.button_scale_targets[button_id] = 1.0

    def button_hover(self, button_id: str) -> None:
        """Trigger button hover animation."""
        if button_id not in self.button_scale_targets:
            self.button_scale_targets[button_id] = 1.05

    def button_unhover(self, button_id: str) -> None:
        """Remove button hover."""
        if button_id in self.button_scale_targets:
            self.button_scale_targets[button_id] = 1.0

    def update(self, dt: float) -> None:
        """Update all button animations."""
        for button_id, target in self.button_scale_targets.items():
            current = self.button_scales.get(button_id, 1.0)

            if abs(current - target) < 0.01:
                self.button_scales[button_id] = target
            else:
                # Lerp toward target
                self.button_scales[button_id] = current + (target - current) * self.scale_speed * dt

    def get_button_scale(self, button_id: str) -> float:
        """Get current scale for a button."""
        return self.button_scales.get(button_id, 1.0)
