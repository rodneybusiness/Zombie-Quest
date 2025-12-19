# Game Juice - Quick Start Cheat Sheet

Copy-paste these exact code blocks for instant game feel improvements.

## 1. Add Import to engine.py (Line 1)

```python
from .juice import (
    HitstopManager, KnockbackManager, CameraTrauma,
    BobbingCamera, ScreenPulse, FootstepTimer, NumberTicker
)
from .effects import RedVignette, DustPuffEmitter
```

## 2. Add to engine.py GameEngine.__init__() (After line 82)

```python
# Juice systems
self.hitstop = HitstopManager()
self.hero_knockback = KnockbackManager()
self.camera_trauma = CameraTrauma()
self.camera_bob = BobbingCamera(amplitude=1.5, smoothness=5.0)
self.screen_pulse = ScreenPulse()
self.red_vignette = RedVignette((WINDOW_SIZE[0], WINDOW_SIZE[1]))
self.dust_emitter = DustPuffEmitter()
self.health_ticker = NumberTicker(initial_value=self.hero.health, tick_speed=8.0)
self.footstep_timer = FootstepTimer(steps_per_cycle=4)
```

## 3. Replace engine.py _damage_hero() method

```python
def _damage_hero(self, amount: int) -> None:
    """Apply damage to hero with full juice effects."""
    if self.hero.take_damage(amount):
        self.state = GameState.GAME_OVER
        self.message_box.show("The neon fades to black...")
        self.audio.play("error")
        self.camera_trauma.add_trauma(1.0)
    else:
        # HITSTOP: 2 frames
        self.hitstop.trigger(frames=2)

        # KNOCKBACK
        if self.current_room.zombies:
            hero_pos = self.hero.position
            nearest_zombie = min(
                self.current_room.zombies,
                key=lambda z: (pygame.Vector2(z.position) - hero_pos).length()
            )
            knockback_dir = hero_pos - pygame.Vector2(nearest_zombie.position)
            self.hero_knockback.apply(knockback_dir, strength=150.0, duration=0.25)

        # CAMERA SHAKE
        self.camera_trauma.add_trauma(0.6)

        self.audio.play("hit")
        self.particles.emit_damage(self.hero.position.x, self.hero.position.y - 20)
        self.health_ticker.set_target(self.hero.health)
```

## 4. Add to top of engine.py update() method

```python
def update(self, dt: float) -> None:
    """Update game state with juice."""
    # HITSTOP CHECK - freezes game
    if self.hitstop.is_frozen():
        self.hitstop.update()
        return

    # Update effects
    self.camera_trauma.update(dt)
    self.screen_pulse.update(dt)
    self.red_vignette.update(dt)
    self.dust_emitter.update(dt)
    # ... rest of existing update code ...
```

## 5. Add knockback handling in engine.py update() (After hero input)

```python
# Apply knockback to hero (add after hero.handle_keyboard_input(keys))
knockback_offset = self.hero_knockback.update(dt)
if knockback_offset:
    new_pos = self.hero.position + knockback_offset
    room_rect = pygame.Rect(0, 0, ROOM_WIDTH, ROOM_HEIGHT)
    new_pos.x = max(room_rect.left + 10, min(room_rect.right - 10, new_pos.x))
    new_pos.y = max(room_rect.top + 10, min(room_rect.bottom - 10, new_pos.y))
    self.hero.position = new_pos
```

## 6. Add footstep dust in engine.py update() (After hero.update())

```python
# FOOTSTEP EFFECTS (add after hero.update())
hero_velocity = self.hero.position - old_pos  # Save old_pos before hero.update()
if hero_velocity.length() > 0.5:
    if self.footstep_timer.check_step(self.hero.animation_state.frame_index):
        self.dust_emitter.emit(
            (self.hero.position.x, self.hero.position.y),
            direction=(hero_velocity.x, hero_velocity.y) if hero_velocity.length() > 0 else None
        )
```

## 7. Add red vignette on zombie groans in engine.py _update_room()

```python
# In _update_room() where zombie.should_groan() is checked:
if zombie.should_groan():
    self.audio.play("zombie_groan", volume=0.3)
    self.red_vignette.trigger(intensity=0.25, duration=0.6)  # ADD THIS LINE
```

## 8. Replace engine.py draw() camera shake section

```python
def draw(self) -> None:
    """Render with camera effects."""
    # Get camera offsets
    trauma_x, trauma_y, trauma_rot = self.camera_trauma.update(0)

    # Get camera bob
    hero_velocity = pygame.Vector2(0, 0)
    if hasattr(self.hero, 'keyboard_velocity'):
        hero_velocity = self.hero.keyboard_velocity * GAMEPLAY.HERO_SPEED
    elif self.hero.current_target:
        to_target = self.hero.current_target - self.hero.position
        hero_velocity = to_target.normalize() * GAMEPLAY.HERO_SPEED if to_target.length() > 0 else pygame.Vector2(0, 0)

    bob_x, bob_y = self.camera_bob.update(1/60.0, hero_velocity)

    shake_x = int(trauma_x + bob_x)
    shake_y = int(trauma_y + bob_y)

    # Clear and draw
    self.screen.fill((0, 0, 0))
    self.current_room.draw(self.room_surface, self.hero)
    self.particles.draw(self.room_surface)
    self.dust_emitter.draw(self.room_surface)  # ADD THIS

    # Blit with shake
    self.screen.blit(self.room_surface, (shake_x, UI_BAR_HEIGHT + shake_y))

    # Draw UI with ticking health
    display_health = self.health_ticker.update(0)
    self.verb_bar.draw(self.screen, display_health)
    # ... rest of UI drawing ...

    self.red_vignette.draw(self.screen)  # ADD BEFORE TRANSITION
    self.transition.draw(self.screen)
    self.scanlines.draw(self.screen)
```

## 9. Add squash/stretch to Hero in characters.py

In Hero.__init__() (after line 141):
```python
from .juice import SquashStretch
self.squash_stretch = SquashStretch(max_deform=0.05)
self.last_velocity = pygame.Vector2(0, 0)
```

In Hero.draw() (replace method):
```python
def draw(self, surface: pygame.Surface, room_height: int) -> pygame.Rect:
    """Draw hero with squash/stretch."""
    if self.is_invincible and int(self.flash_timer * 10) % 2 == 0:
        return pygame.Rect(0, 0, 0, 0)

    # Get velocity for squash/stretch
    current_velocity = pygame.Vector2(0, 0)
    if hasattr(self, 'keyboard_velocity') and self.using_keyboard:
        current_velocity = self.keyboard_velocity * self.speed
    elif self.current_target:
        to_target = self.current_target - self.position
        if to_target.length() > 0:
            current_velocity = to_target.normalize() * self.speed

    scale_x, scale_y = self.squash_stretch.update(1/60.0, current_velocity)

    frame = self.current_frame
    scale = self.compute_scale(room_height)
    width = max(1, int(frame.get_width() * scale * scale_x))
    height = max(1, int(frame.get_height() * scale * scale_y))
    scaled = pygame.transform.scale(frame, (width, height))
    draw_pos = (int(self.position.x - width // 2), int(self.position.y - height))
    surface.blit(scaled, draw_pos)
    return pygame.Rect(draw_pos, (width, height))
```

## 10. Add button hover to VerbBar in ui.py

In VerbBar.__init__() (after line 243):
```python
from .juice import ease_out_cubic
self.hover_scales = {verb: 1.0 for verb, _, _ in self.verb_icons}
self.target_scales = {verb: 1.0 for verb, _, _ in self.verb_icons}
self.ease_out_cubic = ease_out_cubic
```

Add method to VerbBar:
```python
def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
    """Update hover animations."""
    self.update_hover(mouse_pos)
    for verb, icon, rect in self.verb_icons:
        if verb == self.hovered_verb:
            self.target_scales[verb] = 1.1
        else:
            self.target_scales[verb] = 1.0
        current = self.hover_scales[verb]
        target = self.target_scales[verb]
        self.hover_scales[verb] += (target - current) * 15.0 * dt
```

In VerbBar.draw(), replace icon drawing loop:
```python
for verb, icon_surface, icon_rect in self.verb_icons:
    # Apply hover scale
    scale = self.hover_scales.get(verb, 1.0)
    if scale != 1.0:
        scaled_w = int(icon_surface.get_width() * scale)
        scaled_h = int(icon_surface.get_height() * scale)
        scaled_icon = pygame.transform.scale(icon_surface, (scaled_w, scaled_h))
        scaled_rect = scaled_icon.get_rect(center=icon_rect.center)
        surface.blit(scaled_icon, scaled_rect)
    else:
        surface.blit(icon_surface, icon_rect)
    # ... rest of drawing code
```

## 11. Call VerbBar.update() in engine.py

In engine.py handle_events() (after line 130):
```python
# Update verb bar animations
self.verb_bar.update(dt, mouse_pos)
```

## That's It!

These 11 copy-paste blocks give you:
- ✓ Hitstop on damage (2-frame freeze)
- ✓ Knockback physics
- ✓ Camera trauma shake
- ✓ Camera bobbing
- ✓ Footstep dust particles
- ✓ Red vignette on danger
- ✓ Squash/stretch characters
- ✓ Button hover scaling
- ✓ Health number ticking

Run the game and feel the difference immediately!

## Exact Timing Reference

```python
# Combat
hitstop.trigger(frames=2)                    # 33ms freeze
knockback.apply(dir, strength=150, duration=0.25)
camera_trauma.add_trauma(0.6)                # 0.3=small, 0.6=medium, 1.0=huge

# Camera
BobbingCamera(amplitude=1.5, smoothness=5.0)

# UI
scale = 1.1                                   # 10% hover growth
NumberTicker(tick_speed=8.0)                  # 8 numbers/second

# Environmental
red_vignette.trigger(intensity=0.25, duration=0.6)
```

## Test Checklist
- [ ] Take damage → game freezes briefly, hero pushed back, screen shakes
- [ ] Walk around → subtle dust puffs, camera bobs slightly
- [ ] Hover verb button → button grows 10%
- [ ] Zombie groans → red edges pulse
- [ ] Hero turns → subtle squash/stretch (hard to see but feels better)
- [ ] Health changes → numbers count up/down smoothly

If all checked, juice is working! 🎮✨
