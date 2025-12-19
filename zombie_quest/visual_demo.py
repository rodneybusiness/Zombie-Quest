#!/usr/bin/env python3
"""Visual enhancements demo - showcases all 8 new visual features.

Run this to see all visual improvements in action:
- Sprite caching
- Drop shadows
- 8-direction movement
- Idle animations
- Neon glow lighting
- CRT shader
- Parallax backgrounds

Usage:
    python zombie_quest/visual_demo.py
"""
from __future__ import annotations

import pygame
import sys
import math
from typing import Tuple

# Import all visual systems
from .sprite_config import PROPORTIONS, HERO_COLORS, SHADOW_CONFIG
from .sprite_cache import SpriteCache, get_global_cache
from .shadow_renderer import ShadowRenderer
from .eight_direction import EightDirectionSystem, create_eight_direction_animations
from .idle_animation import IdleAnimationGenerator, IdleAnimationController, IDLE_CONFIG
from .neon_lighting import NeonLightingSystem, NeonLight, create_neon_sign_lights
from .crt_shader import CRTShader, CRTConfig
from .parallax_backgrounds import ParallaxBackground, ParallaxLayer
from .sprites import create_detailed_hero_sprite, create_detailed_zombie_sprite
from .backgrounds import create_hennepin_background


class VisualDemo:
    """Interactive demo of all visual enhancements."""

    def __init__(self):
        pygame.init()

        # Screen setup
        self.screen_size = (960, 720)  # 3x scale for visibility
        self.render_size = (320, 240)  # Internal render size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Zombie Quest - Visual Enhancements Demo")

        # Render surface
        self.render_surface = pygame.Surface(self.render_size)

        # Clock
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.time = 0.0

        # Feature toggles (press number keys to toggle)
        self.features = {
            '1': ('shadows', True),
            '2': ('neon_lighting', True),
            '3': ('crt_shader', True),
            '4': ('parallax', True),
            '5': ('idle_animation', True),
            '6': ('eight_direction', True),
        }

        # Initialize visual systems
        self._init_visual_systems()

        # Demo character
        self.hero_pos = pygame.Vector2(160, 120)
        self.hero_direction = "down"
        self.hero_moving = False
        self.hero_frame = 0
        self.hero_frame_time = 0.0

        # Demo zombie
        self.zombie_pos = pygame.Vector2(240, 100)

        # Camera for parallax
        self.camera_pos = pygame.Vector2(160, 120)

        # Info text
        self.font = pygame.font.Font(None, 20)

    def _init_visual_systems(self):
        """Initialize all visual enhancement systems."""
        # 1. Sprite cache
        self.sprite_cache = get_global_cache()

        # 2. Shadow renderer
        self.shadow_renderer = ShadowRenderer()

        # 3. 8-direction animations
        if self.features['6'][1]:  # eight_direction enabled
            self.hero_animations = create_eight_direction_animations(
                create_detailed_hero_sprite,
                scale=2.5
            )
            self.zombie_animations = create_eight_direction_animations(
                lambda d, f, s: create_detailed_zombie_sprite(d, f, "scene", s),
                scale=2.5
            )
        else:
            # Regular 4-direction
            from .sprites import create_hero_animations, create_zombie_animations
            self.hero_animations = create_hero_animations(scale=2.5)
            self.zombie_animations = create_zombie_animations(zombie_type="scene", scale=2.5)

        # 4. Idle animations
        if self.features['5'][1]:  # idle_animation enabled
            idle_gen = IdleAnimationGenerator()
            hero_idle = idle_gen.create_idle_animation_set(
                create_detailed_hero_sprite,
                ["up", "down", "left", "right", "up_left", "up_right", "down_left", "down_right"]
                if self.features['6'][1] else ["up", "down", "left", "right"],
                scale=2.5
            )
            self.hero_idle_controller = IdleAnimationController(hero_idle)
        else:
            self.hero_idle_controller = None

        # 5. Neon lighting
        self.neon_lighting = NeonLightingSystem(self.render_size)
        self._setup_neon_lights()

        # 6. CRT shader
        crt_config = CRTConfig(
            scanline_intensity=0.15,
            curvature_enabled=True,
            curvature_amount=0.12,
            chromatic_aberration=True,
            aberration_amount=1.0,
            phosphor_glow=True,
            glow_intensity=0.25,
            vignette_enabled=True,
            vignette_intensity=0.3,
            noise_enabled=True,
            noise_intensity=0.05,
        )
        self.crt_shader = CRTShader(self.render_size, crt_config)

        # 7. Parallax background
        self.parallax = ParallaxBackground(self.render_size)
        self._setup_parallax()

    def _setup_neon_lights(self):
        """Setup neon signs for demo."""
        # "ZOMBIE QUEST" sign
        lights = create_neon_sign_lights(
            "ZOMBIE QUEST",
            position=(90, 20),
            color=(255, 100, 200),
            char_width=10,
        )
        for light in lights:
            self.neon_lighting.add_light(light)

        # "DEMO" sign
        lights = create_neon_sign_lights(
            "DEMO",
            position=(140, 40),
            color=(100, 255, 200),
            char_width=12,
        )
        for light in lights:
            self.neon_lighting.add_light(light)

        # Ambient street lights
        for x in [60, 260]:
            self.neon_lighting.add_light(NeonLight(
                position=(x, 80),
                color=(255, 240, 200),
                intensity=0.6,
                radius=50,
                flicker=False,
            ))

    def _setup_parallax(self):
        """Setup parallax background layers."""
        # Far layer (sky)
        far_layer = pygame.Surface(self.render_size)
        pygame.draw.rect(far_layer, (10, 5, 30), (0, 0, *self.render_size))
        for i in range(50):
            import random
            x = random.randint(0, self.render_size[0])
            y = random.randint(0, 100)
            far_layer.set_at((x, y), (200, 200, 255))

        self.parallax.add_layer(ParallaxLayer(
            surface=far_layer,
            depth=0.0,
            scroll_factor=0.1,
            wrap_horizontal=True,
        ))

        # Mid layer (buildings)
        mid_layer = create_hennepin_background(self.render_size)
        self.parallax.add_layer(ParallaxLayer(
            surface=mid_layer,
            depth=0.5,
            scroll_factor=0.5,
        ))

        # Fore layer (street details)
        fore_layer = pygame.Surface(self.render_size, pygame.SRCALPHA)
        # Add some foreground elements
        pygame.draw.rect(fore_layer, (60, 55, 75), (10, 180, 20, 50))  # Kiosk
        self.parallax.add_layer(ParallaxLayer(
            surface=fore_layer,
            depth=1.0,
            scroll_factor=1.0,
        ))

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        # Movement (WASD or arrows)
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 or dy != 0:
            velocity = pygame.Vector2(dx, dy).normalize()
            self.hero_pos += velocity * 100 * self.dt
            self.camera_pos += velocity * 50 * self.dt  # Camera follows
            self.hero_moving = True

            # Update direction
            if self.features['6'][1]:  # 8-direction
                self.hero_direction = EightDirectionSystem.vector_to_direction((dx, dy))
            else:
                # 4-direction
                if abs(dx) > abs(dy):
                    self.hero_direction = "right" if dx > 0 else "left"
                else:
                    self.hero_direction = "down" if dy > 0 else "up"
        else:
            self.hero_moving = False

        # Feature toggles
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.unicode in self.features:
                    name, enabled = self.features[event.unicode]
                    self.features[event.unicode] = (name, not enabled)
                    print(f"{name}: {'ON' if not enabled else 'OFF'}")

        return True

    def update(self):
        """Update demo state."""
        self.dt = self.clock.tick(60) / 1000.0
        self.time += self.dt

        # Update parallax
        if self.features['4'][1]:  # parallax enabled
            self.parallax.update((self.camera_pos.x, self.camera_pos.y), self.dt)

        # Update neon lighting
        if self.features['2'][1]:  # neon_lighting enabled
            self.neon_lighting.update(self.dt)

        # Update hero animation
        if self.hero_moving:
            self.hero_frame_time += self.dt
            if self.hero_frame_time >= 0.15:
                self.hero_frame_time = 0.0
                self.hero_frame = (self.hero_frame + 1) % 4
        else:
            self.hero_frame = 0

        # Update idle animation
        if self.hero_idle_controller and self.features['5'][1]:
            self.hero_idle_controller.update(self.dt, self.hero_moving, frame_duration=0.2)

    def render(self):
        """Render demo."""
        # Clear render surface
        self.render_surface.fill((0, 0, 0))

        # 1. Render parallax background
        if self.features['4'][1]:
            self.parallax.render(self.render_surface)
        else:
            # Simple background
            bg = create_hennepin_background(self.render_size)
            self.render_surface.blit(bg, (0, 0))

        # 2. Render neon lighting
        if self.features['2'][1]:
            self.neon_lighting.render_lighting(self.render_surface)

        # 3. Render characters
        self._render_character(self.hero_pos, self.hero_direction, self.hero_frame, is_hero=True)
        self._render_character(self.zombie_pos, "down", int(self.time * 2) % 4, is_hero=False)

        # 4. Render info text
        self._render_info()

        # 5. Apply CRT shader
        if self.features['3'][1]:
            final = self.crt_shader.apply_crt_effect(self.render_surface)
        else:
            final = self.render_surface

        # 6. Scale to screen
        scaled = pygame.transform.scale(final, self.screen_size)
        self.screen.blit(scaled, (0, 0))

        pygame.display.flip()

    def _render_character(self, pos: pygame.Vector2, direction: str, frame: int, is_hero: bool):
        """Render a character with all features."""
        # Get sprite
        if is_hero:
            animations = self.hero_animations
            # Use idle animation if not moving
            if not self.hero_moving and self.hero_idle_controller and self.features['5'][1]:
                sprite = self.hero_idle_controller.get_idle_frame(direction)
            else:
                frames = animations.get(direction, animations.get("down", []))
                sprite = frames[frame % len(frames)] if frames else None
        else:
            animations = self.zombie_animations
            frames = animations.get(direction, animations.get("down", []))
            sprite = frames[frame % len(frames)] if frames else None

        if sprite is None:
            return

        # Calculate depth ratio for shadow
        depth_ratio = pos.y / float(self.render_size[1])

        # Render with or without shadow
        if self.features['1'][1]:  # shadows enabled
            foot_pos = (int(pos.x), int(pos.y))
            self.shadow_renderer.render_character_with_shadow(
                self.render_surface,
                sprite,
                foot_pos,
                depth_ratio
            )
        else:
            # Simple blit
            rect = sprite.get_rect(midbottom=(int(pos.x), int(pos.y)))
            self.render_surface.blit(sprite, rect.topleft)

    def _render_info(self):
        """Render info overlay."""
        y = 5
        info_lines = [
            "Visual Enhancements Demo",
            "",
            "Controls:",
            "WASD/Arrows - Move",
            "1 - Shadows",
            "2 - Neon Lighting",
            "3 - CRT Shader",
            "4 - Parallax",
            "5 - Idle Animation",
            "6 - 8-Direction",
            "ESC - Quit",
            "",
            "Features:",
        ]

        for name, enabled in self.features.values():
            status = "ON" if enabled else "OFF"
            info_lines.append(f"{name}: {status}")

        # Create semi-transparent overlay
        info_surface = pygame.Surface((150, len(info_lines) * 15), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 180))

        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (255, 255, 255))
            info_surface.blit(text, (5, i * 15))

        self.render_surface.blit(info_surface, (5, 5))

    def run(self):
        """Run the demo."""
        print("=" * 60)
        print("Zombie Quest - Visual Enhancements Demo")
        print("=" * 60)
        print("\nShowcasing 8 new visual features:")
        print("1. Sprite Config Extraction")
        print("2. Sprite Cache System")
        print("3. Drop Shadow System")
        print("4. 8-Direction Movement")
        print("5. Idle Animation")
        print("6. Neon Glow Lighting")
        print("7. CRT Shader")
        print("8. Parallax Backgrounds")
        print("\nPress number keys to toggle features!")
        print("Move with WASD or arrow keys.")
        print("=" * 60)

        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()

        pygame.quit()
        print("\nDemo finished. Thanks for watching!")


def main():
    """Run the visual demo."""
    try:
        demo = VisualDemo()
        demo.run()
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
