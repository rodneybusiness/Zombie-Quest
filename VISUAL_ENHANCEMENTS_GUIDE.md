# Visual Enhancements Integration Guide

Complete guide to integrating world-class visual features into Zombie Quest.

## Overview

This guide shows how to integrate 8 major visual systems:

1. **Sprite Config Extraction** - Centralized configuration
2. **Sprite Cache System** - Zero regeneration overhead
3. **Drop Shadow System** - Proper character grounding
4. **8-Direction Movement** - Diagonal sprites
5. **Idle Animation** - Breathing and subtle movement
6. **Neon Glow Lighting** - Additive blending on surfaces
7. **CRT Shader** - Authentic retro display effects
8. **Parallax Backgrounds** - Multi-layer depth

---

## 1. Sprite Config Integration

### File: `zombie_quest/sprite_config.py`

**Purpose**: Extracts all magic numbers from sprite generation into configurable constants.

**Integration Steps**:

1. Import config in `sprites.py`:
```python
from .sprite_config import (
    PROPORTIONS, HERO_COLORS, ANIMATION_FRAMES,
    IDLE_CONFIG, SHADOW_CONFIG, DIAGONAL_CONFIG
)
```

2. Replace magic numbers with config values:
```python
# Before:
surface = pygame.Surface((16, 32), pygame.SRCALPHA)

# After:
surface = pygame.Surface(
    (PROPORTIONS.BASE_WIDTH, PROPORTIONS.BASE_HEIGHT),
    pygame.SRCALPHA
)
```

3. Use color config:
```python
# Before:
SKIN = (255, 210, 180)

# After:
from .sprite_config import HERO_COLORS
p = HERO_COLORS
draw_rect(x, y, w, h, p.SKIN)
```

---

## 2. Sprite Cache Integration

### File: `zombie_quest/sprite_cache.py`

**Purpose**: Prevents sprite regeneration, massive performance boost.

**Integration in `characters.py`**:

```python
from .sprite_cache import get_global_cache

class Hero(Character):
    def __init__(self, position: WorldPos) -> None:
        cache = get_global_cache()

        # Get cached animations (generated once)
        animations = cache.get_animation_set(
            char_type="hero",
            generator_func=create_hero_animations,
            scale=2.5
        )

        super().__init__("Frontperson", position, animations, speed=GAMEPLAY.HERO_SPEED)
        # ... rest of init
```

**For zombies**:

```python
class Zombie(Character):
    def __init__(self, position: WorldPos, zombie_type: str = "scene") -> None:
        cache = get_global_cache()

        char_type = f"zombie_{zombie_type}"
        animations = cache.get_animation_set(
            char_type=char_type,
            generator_func=lambda **kwargs: create_zombie_animations(
                zombie_type=zombie_type,
                scale=kwargs.get('scale', 2.5)
            ),
            scale=2.5
        )

        super().__init__(
            f"{zombie_type.title()} Zombie",
            position,
            animations,
            speed=GAMEPLAY.ZOMBIE_SPEED
        )
```

**Preloading (optional, in loading screen)**:

```python
def preload_sprites():
    """Call during loading screen."""
    cache = get_global_cache()

    # Preload hero
    cache.preload_character(
        "hero",
        ["up", "down", "left", "right"],
        frame_count=4,
        scale=2.5,
        generator_func=create_detailed_hero_sprite
    )

    # Preload zombies
    for ztype in ["scene", "bouncer", "rocker", "dj"]:
        cache.preload_character(
            f"zombie_{ztype}",
            ["up", "down", "left", "right"],
            frame_count=4,
            scale=2.5,
            generator_func=lambda d, f, s, t=ztype: create_detailed_zombie_sprite(
                d, f, t, s
            )
        )
```

---

## 3. Drop Shadow Integration

### File: `zombie_quest/shadow_renderer.py`

**Purpose**: Adds proper drop shadows under all characters.

**Integration in `characters.py`**:

```python
from .shadow_renderer import ShadowRenderer

class Character:
    def __init__(self, name, position, animations, speed=60.0):
        # ... existing init ...
        self.shadow_renderer = ShadowRenderer()

    def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
        """Draw character with drop shadow."""
        frame = self.current_frame
        scale = self.compute_scale(room_height)

        width = max(1, int(frame.get_width() * scale))
        height = max(1, int(frame.get_height() * scale))
        scaled = pygame.transform.scale(frame, (width, height))

        # Calculate depth ratio for shadow perspective
        depth_ratio = max(0.0, min(1.0, self.position.y / float(room_height)))

        # Position at character's feet
        foot_pos = (int(self.position.x), int(self.position.y))

        # Render with shadow
        return self.shadow_renderer.render_character_with_shadow(
            surface, scaled, foot_pos, depth_ratio
        )
```

---

## 4. 8-Direction Movement Integration

### File: `zombie_quest/eight_direction.py`

**Purpose**: Adds diagonal movement with proper sprites.

**Integration in `characters.py`**:

```python
from .eight_direction import (
    EightDirectionSystem,
    create_eight_direction_animations
)

class Character:
    def _update_direction(self, motion: pygame.Vector2) -> None:
        """Update facing direction (now supports 8 directions)."""
        if motion.length_squared() == 0:
            return

        # Convert to 8 directions
        direction = EightDirectionSystem.vector_to_direction((motion.x, motion.y))
        self.animation_state.direction = direction

class Hero(Character):
    def __init__(self, position: WorldPos) -> None:
        # Use 8-direction animations
        from .sprites import create_detailed_hero_sprite

        animations = create_eight_direction_animations(
            create_detailed_hero_sprite,
            scale=2.5
        )

        super().__init__("Frontperson", position, animations, speed=GAMEPLAY.HERO_SPEED)
        # ... rest of init
```

---

## 5. Idle Animation Integration

### File: `zombie_quest/idle_animation.py`

**Purpose**: Breathing and subtle movement when stationary.

**Integration in `characters.py`**:

```python
from .idle_animation import IdleAnimationGenerator, IdleAnimationController, IDLE_CONFIG

class Character:
    def __init__(self, name, position, animations, speed=60.0):
        # ... existing init ...
        self.idle_animations = None
        self.idle_controller = None

    def setup_idle_animations(self, base_generator: callable, scale: float = 2.5):
        """Setup idle animations."""
        if IDLE_CONFIG.ENABLED:
            generator = IdleAnimationGenerator()
            directions = ["up", "down", "left", "right"]  # Or 8 directions

            self.idle_animations = generator.create_idle_animation_set(
                base_generator, directions, scale
            )
            self.idle_controller = IdleAnimationController(self.idle_animations)

    def update_animation(self, dt: float, moving: bool) -> None:
        """Update animation with idle support."""
        # Update idle controller
        if self.idle_controller:
            self.idle_controller.update(dt, moving, frame_duration=0.2)

        direction = self.animation_state.direction
        frames = self.animations.get(direction, [])

        # Use idle animation when not moving
        if not moving and self.idle_controller and self.idle_animations:
            idle_frame = self.idle_controller.get_idle_frame(direction)
            if idle_frame:
                self.current_frame = idle_frame
                self.idle = True
                return

        # Use walk animation (existing code)
        if moving:
            self.animation_state.frame_time += dt
            if self.animation_state.frame_time >= ANIMATION.FRAME_DURATION:
                self.animation_state.frame_time -= ANIMATION.FRAME_DURATION
                self.animation_state.frame_index = (
                    (self.animation_state.frame_index + 1) % len(frames)
                )
        else:
            self.animation_state.frame_index = 0

        if frames:
            index = min(self.animation_state.frame_index, len(frames) - 1)
            self.current_frame = frames[index]
        self.idle = not moving

class Hero(Character):
    def __init__(self, position):
        # ... existing init ...

        # Setup idle animations
        from .sprites import create_detailed_hero_sprite
        self.setup_idle_animations(create_detailed_hero_sprite, scale=2.5)
```

---

## 6. Neon Glow Lighting Integration

### File: `zombie_quest/neon_lighting.py`

**Purpose**: Makes neon signs illuminate nearby surfaces with additive blending.

**Integration in `ui.py` or `engine.py`**:

```python
from .neon_lighting import NeonLightingSystem, NeonBackgroundMixin

class GameRenderer(NeonBackgroundMixin):
    def __init__(self, screen_size):
        self.neon_lighting = NeonLightingSystem(screen_size)
        self.screen_size = screen_size
        # ... rest of init

    def render_room(self, surface, room_id, background, dt):
        # 1. Draw background
        surface.blit(background, (0, 0))

        # 2. Setup and render neon lights
        self.setup_neon_lights(room_id, self.neon_lighting)
        self.neon_lighting.update(dt)
        self.neon_lighting.render_lighting(surface)

        # 3. Draw characters (they'll be lit by neon)
        # ... draw characters ...

        # 4. Draw foreground elements
        # ... draw foreground ...
```

---

## 7. CRT Shader Integration

### File: `zombie_quest/crt_shader.py`

**Purpose**: Authentic 1980s CRT monitor effects.

**Integration in main render loop**:

```python
from .crt_shader import CRTShader, CRTConfig

class GameEngine:
    def __init__(self):
        # ... existing init ...

        # Create CRT shader
        crt_config = CRTConfig(
            scanline_intensity=0.15,
            curvature_enabled=True,
            curvature_amount=0.12,
            chromatic_aberration=True,
            aberration_amount=1.0,
            phosphor_glow=True,
            glow_intensity=0.25,
        )

        self.crt_shader = CRTShader((DISPLAY.ROOM_WIDTH, DISPLAY.ROOM_HEIGHT), crt_config)

    def render(self):
        # Render game to internal surface
        game_surface = pygame.Surface((DISPLAY.ROOM_WIDTH, DISPLAY.ROOM_HEIGHT))

        # ... render everything to game_surface ...

        # Apply CRT effect
        final_surface = self.crt_shader.apply_crt_effect(game_surface)

        # Scale up and display
        scaled = pygame.transform.scale(
            final_surface,
            (DISPLAY.ROOM_WIDTH * DISPLAY.SCALE_FACTOR,
             DISPLAY.ROOM_HEIGHT * DISPLAY.SCALE_FACTOR)
        )

        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
```

---

## 8. Parallax Backgrounds Integration

### File: `zombie_quest/parallax_backgrounds.py`

**Purpose**: Multi-layer depth with camera-relative scrolling.

**Integration in `rooms.py` or `engine.py`**:

```python
from .parallax_backgrounds import ParallaxBackground, split_background_into_layers

class Room:
    def __init__(self, room_id, size=(320, 200)):
        self.room_id = room_id

        # Create parallax background system
        self.parallax = ParallaxBackground(size)

        # Generate and add layers
        from .backgrounds import get_room_background
        layers = split_background_into_layers(
            get_room_background,
            room_id,
            size
        )

        for layer in layers:
            self.parallax.add_layer(layer)

    def update(self, camera_position, dt):
        """Update room with camera position."""
        self.parallax.update(camera_position, dt)

    def render(self, surface):
        """Render room background."""
        self.parallax.render(surface)

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
```

---

## Complete Integration Example

Here's how everything works together in `engine.py`:

```python
from .sprite_cache import get_global_cache, clear_global_cache
from .shadow_renderer import ShadowRenderer
from .neon_lighting import NeonLightingSystem, NeonBackgroundMixin
from .crt_shader import CRTShader, CRTConfig
from .parallax_backgrounds import ParallaxBackground
from .config import DISPLAY

class GameEngine(NeonBackgroundMixin):
    def __init__(self):
        # ... existing init ...

        # Visual systems
        self.sprite_cache = get_global_cache()
        self.shadow_renderer = ShadowRenderer()
        self.neon_lighting = NeonLightingSystem((DISPLAY.ROOM_WIDTH, DISPLAY.ROOM_HEIGHT))

        # CRT shader
        crt_config = CRTConfig(
            scanline_intensity=0.15,
            curvature_enabled=True,
            phosphor_glow=True,
        )
        self.crt_shader = CRTShader((DISPLAY.ROOM_WIDTH, DISPLAY.ROOM_HEIGHT), crt_config)

    def render(self):
        # 1. Render to internal surface
        game_surface = pygame.Surface((DISPLAY.ROOM_WIDTH, DISPLAY.ROOM_HEIGHT))

        # 2. Render parallax background
        self.current_room.render(game_surface)

        # 3. Setup and render neon lighting
        self.setup_neon_lights(self.current_room.room_id, self.neon_lighting)
        self.neon_lighting.update(self.dt)
        self.neon_lighting.render_lighting(game_surface)

        # 4. Draw characters with shadows
        for character in self.get_all_characters():
            character.draw(game_surface, DISPLAY.ROOM_HEIGHT)

        # 5. Draw UI
        # ... UI rendering ...

        # 6. Apply CRT effect
        final_surface = self.crt_shader.apply_crt_effect(game_surface)

        # 7. Scale and display
        scaled = pygame.transform.scale(
            final_surface,
            (DISPLAY.ROOM_WIDTH * DISPLAY.SCALE_FACTOR,
             DISPLAY.ROOM_HEIGHT * DISPLAY.SCALE_FACTOR)
        )

        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
```

---

## Performance Considerations

1. **Sprite Cache**: Generates sprites once, huge performance gain
2. **Shadow Cache**: Shadows are cached by size
3. **Neon Lighting**: Glow surfaces cached by radius/color/intensity
4. **CRT Shader**: Most expensive effect, use sparingly or make toggleable
5. **Parallax**: Minimal overhead, just offset calculations

## Toggleable Features

Make effects toggleable for performance:

```python
class VisualSettings:
    SHADOWS_ENABLED = True
    NEON_LIGHTING_ENABLED = True
    CRT_SHADER_ENABLED = True
    PARALLAX_ENABLED = True
    IDLE_ANIMATIONS_ENABLED = True
    EIGHT_DIRECTION_ENABLED = False  # More sprites to cache
```

---

## Testing

Run the visual demo:

```bash
python zombie_quest/visual_demo.py
```

This will showcase all visual features in action.

---

## Troubleshooting

**Problem**: Sprites regenerating every frame (slow)
**Solution**: Ensure you're using `get_global_cache()` and caching animations

**Problem**: Shadows appearing in wrong position
**Solution**: Check that `depth_ratio` is calculated correctly from `room_height`

**Problem**: CRT shader too slow
**Solution**: Disable curvature or chromatic aberration, or reduce screen size

**Problem**: Neon lights not visible
**Solution**: Ensure `render_lighting()` is called AFTER background but BEFORE characters

**Problem**: Parallax not moving
**Solution**: Ensure camera position is being updated each frame

---

## Credits

These implementations are based on techniques from:
- Shovel Knight (sprite work, shadow system)
- Celeste (CRT shader, parallax)
- Streets of Rage 2 (idle animations)
- Hotline Miami (neon lighting)
