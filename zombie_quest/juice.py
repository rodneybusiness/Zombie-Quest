"""Game juice systems - timing curves, hitstop, knockback, and visual polish.

This module contains all the "game feel" enhancements that make the game responsive
and satisfying to play. Inspired by Vlambeer's screenshake philosophy.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

import pygame


# ============================================================================
# TIMING CURVES / EASING FUNCTIONS
# ============================================================================

def ease_linear(t: float) -> float:
    """Linear interpolation (no easing)."""
    return t


def ease_in_quad(t: float) -> float:
    """Quadratic ease-in (slow start)."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out (slow end)."""
    return t * (2 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out (smooth both ends)."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


def ease_in_cubic(t: float) -> float:
    """Cubic ease-in (very slow start)."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out (very slow end)."""
    return 1 + (t - 1) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out (smooth acceleration/deceleration)."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 + (t - 1) * (2 * (t - 2)) ** 2


def ease_out_bounce(t: float) -> float:
    """Bouncing ease-out (overshoot and bounce back)."""
    if t < 4 / 11:
        return (121 * t * t) / 16
    elif t < 8 / 11:
        return (363 / 40.0 * t * t) - (99 / 10.0 * t) + 17 / 5.0
    elif t < 9 / 10:
        return (4356 / 361.0 * t * t) - (35442 / 1805.0 * t) + 16061 / 1805.0
    return (54 / 5.0 * t * t) - (513 / 25.0 * t) + 268 / 25.0


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out (rubber band effect)."""
    if t == 0 or t == 1:
        return t
    p = 0.3
    s = p / 4
    return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


def ease_in_back(t: float) -> float:
    """Back ease-in (pull back before moving forward)."""
    s = 1.70158
    return t * t * ((s + 1) * t - s)


def ease_out_back(t: float) -> float:
    """Back ease-out (overshoot target)."""
    s = 1.70158
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_in_out_back(t: float) -> float:
    """Back ease-in-out (pull back at start, overshoot at end)."""
    s = 1.70158 * 1.525
    t *= 2
    if t < 1:
        return 0.5 * (t * t * ((s + 1) * t - s))
    t -= 2
    return 0.5 * (t * t * ((s + 1) * t + s) + 2)


# ============================================================================
# HITSTOP SYSTEM
# ============================================================================

class HitstopManager:
    """Manages hitstop (frame freeze) for impact moments.

    When damage occurs, freeze the game for a few frames to emphasize impact.
    This is crucial for combat feel - think of it as a micro-cutscene.
    """

    def __init__(self) -> None:
        self.frozen = False
        self.freeze_frames = 0
        self.frame_counter = 0
        self.is_heavy_hit = False

    def trigger(self, frames: int = 6, hit_type: str = "medium") -> None:
        """Trigger a hitstop freeze.

        Args:
            frames: Number of frames to freeze (at 60fps). 6 frames = 100ms.
            hit_type: "light" (4 frames), "medium" (8 frames), "heavy" (12 frames)
        """
        # Determine frames based on hit type
        if hit_type == "light":
            frames = 4
        elif hit_type == "heavy":
            frames = 12
        elif hit_type == "medium":
            frames = 8

        self.frozen = True
        self.freeze_frames = frames
        self.frame_counter = 0
        self.is_heavy_hit = (hit_type == "heavy")

    def update(self) -> bool:
        """Update hitstop state. Returns True if game should be frozen."""
        if not self.frozen:
            return False

        self.frame_counter += 1
        if self.frame_counter >= self.freeze_frames:
            self.frozen = False
            self.frame_counter = 0
            return False

        return True

    def is_frozen(self) -> bool:
        """Check if game is currently frozen."""
        return self.frozen

    def should_screen_flash(self) -> bool:
        """Check if this hitstop should trigger a screen flash."""
        return self.is_heavy_hit and self.frozen


# ============================================================================
# KNOCKBACK SYSTEM
# ============================================================================

@dataclass
class KnockbackEffect:
    """Represents an active knockback effect on a character."""
    direction: pygame.Vector2  # Direction to push
    strength: float  # Initial strength in pixels/second
    duration: float  # Total duration
    elapsed: float = 0.0
    easing: Callable[[float], float] = ease_out_cubic
    has_landed: bool = False  # Track if ground impact has been triggered
    knockback_type: str = "push"  # "nudge", "push", or "slam"

    def update(self, dt: float) -> Optional[pygame.Vector2]:
        """Update knockback and return displacement vector, or None if finished."""
        if self.elapsed >= self.duration:
            # Trigger landing effect before finishing
            if not self.has_landed:
                self.has_landed = True
            return None

        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)

        # Ease out the knockback (starts strong, fades quickly)
        current_strength = self.strength * (1.0 - self.easing(progress))
        displacement = self.direction * current_strength * dt

        # Check if about to land (90% complete and hasn't landed yet)
        if progress >= 0.9 and not self.has_landed:
            self.has_landed = True

        return displacement

    def should_emit_impact(self) -> bool:
        """Check if ground impact particles should be emitted."""
        return self.has_landed


class KnockbackManager:
    """Manages knockback effects for characters."""

    def __init__(self) -> None:
        self.active_knockback: Optional[KnockbackEffect] = None

    def apply(self, direction: pygame.Vector2, strength: float = 350.0,
              duration: float = 0.25, knockback_type: str = "push") -> None:
        """Apply knockback in a direction.

        Args:
            direction: Direction vector (will be normalized)
            strength: Initial knockback strength in pixels/second
            duration: How long the knockback lasts (0.25s is snappy)
            knockback_type: "nudge" (200), "push" (400), "slam" (600)
        """
        # Determine strength based on knockback type
        if knockback_type == "nudge":
            strength = 200.0
        elif knockback_type == "slam":
            strength = 600.0
        elif knockback_type == "push":
            strength = 400.0

        if direction.length_squared() > 0:
            normalized = direction.normalize()
            self.active_knockback = KnockbackEffect(
                direction=normalized,
                strength=strength,
                duration=duration,
                easing=ease_out_cubic,
                knockback_type=knockback_type
            )

    def update(self, dt: float) -> Optional[pygame.Vector2]:
        """Update and return knockback displacement, or None."""
        if self.active_knockback:
            displacement = self.active_knockback.update(dt)
            if displacement is None:
                self.active_knockback = None
            return displacement
        return None

    def should_emit_impact(self) -> bool:
        """Check if ground impact particles should be emitted."""
        if self.active_knockback and self.active_knockback.should_emit_impact():
            # Reset the flag so we only emit once
            self.active_knockback.has_landed = False
            return True
        return False

    def get_knockback_type(self) -> Optional[str]:
        """Get the type of active knockback."""
        if self.active_knockback:
            return self.active_knockback.knockback_type
        return None

    def clear(self) -> None:
        """Clear any active knockback."""
        self.active_knockback = None


# ============================================================================
# FLASH EFFECT (Hit Feedback)
# ============================================================================

class FlashEffect:
    """White flash effect for enemies when hit."""

    def __init__(self) -> None:
        self.active = False
        self.duration = 0.1  # 100ms flash
        self.elapsed = 0.0
        self.flash_color = (255, 255, 255)  # Pure white

    def trigger(self, duration: float = 0.1) -> None:
        """Trigger a flash effect."""
        self.active = True
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt: float) -> float:
        """Update flash. Returns intensity (0.0-1.0)."""
        if not self.active:
            return 0.0

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return 0.0

        # Flash intensity fades quickly
        progress = self.elapsed / self.duration
        return 1.0 - ease_out_quad(progress)

    def apply_to_surface(self, surface: pygame.Surface, intensity: float) -> pygame.Surface:
        """Apply flash effect to a surface."""
        if intensity <= 0:
            return surface

        # Create a copy and blend with white
        result = surface.copy()
        flash_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(255 * intensity)
        flash_overlay.fill((*self.flash_color, alpha))
        result.blit(flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return result


# ============================================================================
# CAMERA TRAUMA SYSTEM (Enhanced Screen Shake)
# ============================================================================

class CameraTrauma:
    """Trauma-based camera shake system.

    Instead of directly setting shake intensity, you add "trauma" to the camera.
    Trauma decays over time and generates shake. This creates more organic,
    natural-feeling camera movement.

    Inspired by: https://jonathanhickey.com/blog/camera-shake/
    """

    def __init__(self) -> None:
        self.trauma = 0.0  # 0.0 to 1.0
        self.trauma_decay = 2.0  # How fast trauma decays per second
        self.max_offset = 40.0  # Maximum pixel offset (AMPLIFIED from 15)
        self.max_rotation = 2.5  # Maximum rotation in degrees (AMPLIFIED from 0.8)
        self.shake_speed = 20.0  # Frequency of shake oscillation
        self.time = 0.0
        self.trauma_multiplier = 1.0  # Multiplier for proximity effects

    def add_trauma(self, amount: float, multiplier: float = 1.0) -> None:
        """Add trauma to the camera.

        Args:
            amount: Trauma amount (0.0-1.0). 0.3 = small hit, 0.6 = medium, 1.0 = huge
            multiplier: Optional multiplier for proximity effects (e.g., zombie nearby)
        """
        self.trauma_multiplier = max(1.0, multiplier)
        self.trauma = min(1.0, self.trauma + amount * self.trauma_multiplier)

    def update(self, dt: float, zombie_proximity: float = 0.0) -> Tuple[float, float, float]:
        """Update trauma and return (offset_x, offset_y, rotation).

        Args:
            zombie_proximity: 0.0-1.0, how close zombies are (amplifies shake)

        Returns:
            Tuple of (x_offset, y_offset, rotation_degrees)
        """
        if self.trauma <= 0:
            # Decay multiplier when no trauma
            self.trauma_multiplier = max(1.0, self.trauma_multiplier - dt * 2.0)
            return (0.0, 0.0, 0.0)

        # Decay trauma
        self.trauma = max(0.0, self.trauma - self.trauma_decay * dt)

        # Advance time for shake variation
        self.time += dt

        # Proximity multiplier for zombie tension
        proximity_mult = 1.0 + zombie_proximity * 0.5

        # Shake is based on trauma squared (makes small trauma barely noticeable)
        shake = self.trauma * self.trauma * proximity_mult

        # Use Perlin-like noise via sine waves at different frequencies
        offset_x = self.max_offset * shake * math.sin(self.time * self.shake_speed)
        offset_y = self.max_offset * shake * math.sin(self.time * self.shake_speed * 1.3 + 100)
        rotation = self.max_rotation * shake * math.sin(self.time * self.shake_speed * 0.7 + 200)

        return (offset_x, offset_y, rotation)

    def get_trauma(self) -> float:
        """Get current trauma level (0.0-1.0)."""
        return self.trauma


# ============================================================================
# SQUASH AND STRETCH
# ============================================================================

class SquashStretch:
    """Squash and stretch effect for characters.

    AMPLIFIED deformation that makes movement feel PUNCHY and ALIVE.
    12% max deformation is noticeable and adds serious life.
    """

    def __init__(self, max_deform: float = 0.12) -> None:
        self.max_deform = max_deform  # 0.12 = 12% max deformation (AMPLIFIED from 0.05)
        self.current_deform_x = 1.0
        self.current_deform_y = 1.0
        self.target_deform_x = 1.0
        self.target_deform_y = 1.0
        self.spring_strength = 15.0  # How fast it returns to normal
        self.velocity = pygame.Vector2(0, 0)

    def apply_impact(self, direction: pygame.Vector2, strength: float = 1.0) -> None:
        """Apply squash/stretch from an impact or direction change.

        Args:
            direction: Direction of movement (normalized)
            strength: Impact strength (0.0-1.0)
        """
        if direction.length_squared() == 0:
            return

        # Normalize direction
        dir_norm = direction.normalize()

        # Squash in direction of movement, stretch perpendicular
        deform = self.max_deform * strength

        # Horizontal movement: stretch horizontally, squash vertically
        if abs(dir_norm.x) > abs(dir_norm.y):
            self.target_deform_x = 1.0 + deform
            self.target_deform_y = 1.0 - deform
        # Vertical movement: stretch vertically, squash horizontally
        else:
            self.target_deform_x = 1.0 - deform
            self.target_deform_y = 1.0 + deform

    def update(self, dt: float, velocity: pygame.Vector2) -> Tuple[float, float]:
        """Update squash/stretch. Returns (scale_x, scale_y).

        Args:
            dt: Delta time
            velocity: Current velocity for dynamic squash
        """
        # Check for velocity changes (direction changes)
        velocity_change = velocity - self.velocity
        if velocity_change.length() > 50:  # Significant direction change
            if velocity.length_squared() > 0:
                self.apply_impact(velocity, strength=0.3)
        self.velocity = velocity

        # Spring back to normal (1.0, 1.0)
        self.current_deform_x += (self.target_deform_x - self.current_deform_x) * self.spring_strength * dt
        self.current_deform_y += (self.target_deform_y - self.current_deform_y) * self.spring_strength * dt

        # Spring target back to 1.0
        self.target_deform_x += (1.0 - self.target_deform_x) * self.spring_strength * dt
        self.target_deform_y += (1.0 - self.target_deform_y) * self.spring_strength * dt

        return (self.current_deform_x, self.current_deform_y)

    def apply_to_surface(self, surface: pygame.Surface, scale_x: float, scale_y: float) -> pygame.Surface:
        """Apply squash/stretch to a surface."""
        width = max(1, int(surface.get_width() * scale_x))
        height = max(1, int(surface.get_height() * scale_y))
        return pygame.transform.scale(surface, (width, height))


# ============================================================================
# FOOTSTEP TIMING
# ============================================================================

class FootstepTimer:
    """Syncs footstep sounds and effects to animation frames."""

    def __init__(self, steps_per_cycle: int = 4) -> None:
        self.steps_per_cycle = steps_per_cycle  # Typically 4 frames per walk cycle
        self.last_frame = 0
        self.step_frames = [0, 2]  # Which frames trigger footsteps (left, right foot)

    def check_step(self, current_frame: int) -> bool:
        """Check if current frame should trigger a footstep.

        Returns True if this frame is a footstep frame and we haven't triggered it yet.
        """
        if current_frame in self.step_frames and current_frame != self.last_frame:
            self.last_frame = current_frame
            return True
        return False

    def reset(self) -> None:
        """Reset footstep tracking."""
        self.last_frame = -1


# ============================================================================
# NUMBER TICKING (UI)
# ============================================================================

class NumberTicker:
    """Animates numbers counting up/down instead of instant changes."""

    def __init__(self, initial_value: int = 0, tick_speed: float = 8.0) -> None:
        self.current = float(initial_value)
        self.target = initial_value
        self.tick_speed = tick_speed  # Changes per second

    def set_target(self, value: int) -> None:
        """Set new target value."""
        self.target = value

    def update(self, dt: float) -> int:
        """Update ticker. Returns current display value."""
        if abs(self.target - self.current) < 0.1:
            self.current = float(self.target)
            return self.target

        # Move toward target
        diff = self.target - self.current
        step = self.tick_speed * dt

        if abs(diff) < step:
            self.current = float(self.target)
        else:
            self.current += step if diff > 0 else -step

        return int(round(self.current))

    def is_ticking(self) -> bool:
        """Check if currently animating."""
        return abs(self.target - self.current) > 0.1


# ============================================================================
# FLOATING ANIMATION (UI)
# ============================================================================

class FloatingAnimation:
    """Subtle floating/bobbing animation for UI elements."""

    def __init__(self, amplitude: float = 3.0, speed: float = 2.0, phase: float = 0.0) -> None:
        self.amplitude = amplitude  # How many pixels to float
        self.speed = speed  # Cycles per second
        self.time = phase  # Phase offset for staggering

    def update(self, dt: float) -> float:
        """Update animation. Returns Y offset."""
        self.time += dt
        return math.sin(self.time * self.speed * math.pi * 2) * self.amplitude


# ============================================================================
# SLIDE-IN ANIMATION (UI)
# ============================================================================

class SlideInAnimation:
    """Slide-in animation for menu items with stagger."""

    def __init__(self, start_offset: float = 50.0, duration: float = 0.4,
                 stagger_delay: float = 0.05) -> None:
        self.start_offset = start_offset
        self.duration = duration
        self.stagger_delay = stagger_delay
        self.items_progress: dict = {}  # item_id -> progress

    def start_item(self, item_id: int, current_time: float = 0.0) -> None:
        """Start animation for an item with stagger."""
        self.items_progress[item_id] = -self.stagger_delay * item_id

    def update(self, item_id: int, dt: float) -> float:
        """Update item animation. Returns X offset (0 = final position)."""
        if item_id not in self.items_progress:
            return 0.0

        self.items_progress[item_id] += dt
        progress = self.items_progress[item_id]

        if progress < 0:
            return self.start_offset  # Still waiting for stagger
        elif progress >= self.duration:
            return 0.0  # Animation complete
        else:
            # Ease out
            t = progress / self.duration
            return self.start_offset * (1.0 - ease_out_back(t))


# ============================================================================
# ATTENTION PULSE (Objective Markers)
# ============================================================================

class AttentionPulse:
    """Pulsing glow effect to draw attention to important objects."""

    def __init__(self, pulse_speed: float = 1.5, min_intensity: float = 0.4) -> None:
        self.pulse_speed = pulse_speed
        self.min_intensity = min_intensity
        self.time = 0.0

    def update(self, dt: float) -> float:
        """Update pulse. Returns intensity (0.0-1.0)."""
        self.time += dt
        pulse = (math.sin(self.time * self.pulse_speed * math.pi * 2) + 1) / 2
        return self.min_intensity + pulse * (1.0 - self.min_intensity)

    def draw_glow_circle(self, surface: pygame.Surface, pos: Tuple[int, int],
                        radius: int, color: Tuple[int, int, int], intensity: float) -> None:
        """Draw a glowing circle at position."""
        # Draw multiple layers for glow effect
        for i in range(4):
            layer_radius = radius + i * 3
            alpha = int(100 * intensity * (1 - i/4))
            glow_surf = pygame.Surface((layer_radius*2, layer_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, alpha),
                             (layer_radius, layer_radius), layer_radius)
            surface.blit(glow_surf, (pos[0] - layer_radius, pos[1] - layer_radius))


# ============================================================================
# BOUNCE ANIMATION (New Items)
# ============================================================================

class BounceAnimation:
    """Single bounce animation for new inventory items."""

    def __init__(self) -> None:
        self.active = False
        self.elapsed = 0.0
        self.duration = 0.5  # Total bounce time
        self.height = 12.0  # Bounce height in pixels

    def trigger(self) -> None:
        """Start a bounce."""
        self.active = True
        self.elapsed = 0.0

    def update(self, dt: float) -> float:
        """Update bounce. Returns Y offset (negative = up)."""
        if not self.active:
            return 0.0

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return 0.0

        # Bounce curve (parabola with single peak)
        progress = self.elapsed / self.duration
        # Use ease_out_bounce for a realistic bounce
        bounce = ease_out_bounce(progress)
        return -self.height * (1.0 - bounce)


# ============================================================================
# SCREEN PULSE (Audio Sync)
# ============================================================================

class ScreenPulse:
    """Pulse screen on music beats or important moments."""

    def __init__(self) -> None:
        self.active = False
        self.elapsed = 0.0
        self.duration = 0.15  # Quick pulse
        self.intensity = 0.0

    def trigger(self, intensity: float = 0.3) -> None:
        """Trigger a screen pulse.

        Args:
            intensity: Pulse strength (0.0-1.0)
        """
        self.active = True
        self.elapsed = 0.0
        self.intensity = intensity

    def update(self, dt: float) -> float:
        """Update pulse. Returns scale multiplier (e.g., 1.02 = 2% larger)."""
        if not self.active:
            return 1.0

        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return 1.0

        progress = self.elapsed / self.duration
        # Quick expand then return
        pulse_curve = math.sin(progress * math.pi)  # 0 -> 1 -> 0
        return 1.0 + self.intensity * 0.05 * pulse_curve


# ============================================================================
# BOBBING CAMERA (Following Hero)
# ============================================================================

class BobbingCamera:
    """Subtle camera bobbing that follows hero movement."""

    def __init__(self, amplitude: float = 1.5, smoothness: float = 5.0) -> None:
        self.amplitude = amplitude  # Max pixels of bob
        self.smoothness = smoothness  # Interpolation speed
        self.current_offset = pygame.Vector2(0, 0)
        self.target_offset = pygame.Vector2(0, 0)
        self.bob_time = 0.0

    def update(self, dt: float, hero_velocity: pygame.Vector2) -> Tuple[float, float]:
        """Update camera bob based on hero velocity.

        Returns (x_offset, y_offset)
        """
        # Generate bob target based on movement
        if hero_velocity.length_squared() > 10:  # Moving
            self.bob_time += dt * 3.0
            # Bob perpendicular to movement direction
            bob_x = math.sin(self.bob_time) * self.amplitude
            bob_y = math.cos(self.bob_time * 0.5) * self.amplitude * 0.5
            self.target_offset = pygame.Vector2(bob_x, bob_y)
        else:
            # Return to center when stopped
            self.target_offset = pygame.Vector2(0, 0)

        # Smooth interpolation
        self.current_offset += (self.target_offset - self.current_offset) * self.smoothness * dt

        return (self.current_offset.x, self.current_offset.y)
