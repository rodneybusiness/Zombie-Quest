# Game Juice Architecture

Visual guide to understanding how all the juice systems connect.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GAME ENGINE                              │
│                                                                   │
│  ┌─────────────────┐      ┌──────────────────┐                  │
│  │  Input Handler  │──────│   Juice Manager  │                  │
│  └─────────────────┘      └──────────────────┘                  │
│                                    │                             │
│                    ┌───────────────┼───────────────┐             │
│                    ▼               ▼               ▼             │
│            ┌───────────┐   ┌──────────┐   ┌──────────┐          │
│            │  Combat   │   │ Movement │   │    UI    │          │
│            │   Juice   │   │   Juice  │   │   Juice  │          │
│            └───────────┘   └──────────┘   └──────────┘          │
│                    │               │               │             │
│                    └───────────────┼───────────────┘             │
│                                    ▼                             │
│                            ┌───────────────┐                     │
│                            │    Renderer   │                     │
│                            └───────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## Combat Juice Flow

```
Player Takes Damage
        │
        ├─────► HitstopManager.trigger(2)
        │       └──► Freeze game for 2 frames (33ms)
        │
        ├─────► KnockbackManager.apply(direction, 150, 0.25)
        │       └──► Push hero away from zombie
        │
        ├─────► CameraTrauma.add_trauma(0.6)
        │       └──► Screen shakes, decays over time
        │
        ├─────► ParticleSystem.emit_damage(pos)
        │       └──► Red particles burst
        │
        └─────► Audio.play("hit")
                └──► Sound feedback
```

## Movement Juice Flow

```
Hero Walks
        │
        ├─────► SquashStretch.update(velocity)
        │       └──► 5% deformation on direction change
        │
        ├─────► FootstepTimer.check_step(frame)
        │       │
        │       └──► DustPuffEmitter.emit(pos, direction)
        │            └──► 3-5 dust particles
        │
        └─────► BobbingCamera.update(velocity)
                └──► Camera offset (1.5px bob)
```

## UI Juice Flow

```
Hover Button
        │
        └─────► VerbBar.update(dt, mouse_pos)
                │
                ├──► target_scale = 1.1
                │
                └──► current_scale += (target - current) * 15 * dt
                     └──► Smooth interpolation to 110%

Health Changes
        │
        └─────► NumberTicker.set_target(new_health)
                │
                └──► NumberTicker.update(dt)
                     └──► count: 3 → 2.8 → 2.6 → ... → 2
```

## Environmental Effects Flow

```
Room Draw
        │
        ├─────► FlickerLight.update(dt)
        │       └──► intensity = 0.7 + pulse(t) * 0.3
        │
        ├─────► SmokeEmitter.update(dt)
        │       │
        │       ├──► emit_timer >= emit_rate?
        │       │    └──► Create SmokeWisp
        │       │
        │       └──► Update all wisps
        │            └──► Remove dead wisps
        │
        └─────► FlutteringPoster.update(dt)
                └──► position += sin(time) * amplitude
```

## Timing Cascade

```
Frame N: Player hit by zombie
    │
    ├─── t=0.000s: HitstopManager.trigger()
    │              └──► Game freezes
    │
    ├─── t=0.033s: Hitstop ends (2 frames @ 60fps)
    │              KnockbackManager starts
    │              CameraTrauma starts
    │              Particles spawn
    │
    ├─── t=0.100s: Knockback at 60% strength (ease_out_cubic)
    │              Trauma at 80% intensity (decay)
    │              Particles fading
    │
    ├─── t=0.250s: Knockback ends
    │              Trauma at 40% intensity
    │              Most particles gone
    │
    └─── t=0.500s: Trauma at ~10% intensity
                   All effects quiet
```

## Data Flow Diagram

```
┌──────────────┐
│   Player     │
│   Input      │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────────────────┐
│   Engine     │────►│      Juice Systems              │
│   Update()   │     │                                 │
└──────────────┘     │  ┌───────────────────────┐     │
                     │  │ HitstopManager        │     │
                     │  │  - frozen: bool       │     │
                     │  │  - frames_left: int   │     │
                     │  └───────────────────────┘     │
                     │                                 │
                     │  ┌───────────────────────┐     │
                     │  │ KnockbackManager      │     │
                     │  │  - direction: Vec2    │     │
                     │  │  - strength: float    │     │
                     │  │  - elapsed: float     │     │
                     │  └───────────────────────┘     │
                     │                                 │
                     │  ┌───────────────────────┐     │
                     │  │ CameraTrauma          │     │
                     │  │  - trauma: 0.0-1.0    │     │
                     │  │  - time: float        │     │
                     │  └───────────────────────┘     │
                     └─────────────────────────────────┘
                                     │
                                     ▼
                     ┌─────────────────────────────────┐
                     │      Character Update           │
                     │                                 │
                     │  ┌───────────────────────┐     │
                     │  │ Hero.position +=      │     │
                     │  │   knockback_offset    │     │
                     │  └───────────────────────┘     │
                     │                                 │
                     │  ┌───────────────────────┐     │
                     │  │ Hero.draw()           │     │
                     │  │   with squash/stretch │     │
                     │  └───────────────────────┘     │
                     └─────────────────────────────────┘
                                     │
                                     ▼
                     ┌─────────────────────────────────┐
                     │         Renderer                │
                     │                                 │
                     │  camera_offset = trauma + bob   │
                     │  screen.blit(room, offset)      │
                     │                                 │
                     │  particles.draw()               │
                     │  effects.draw()                 │
                     │  ui.draw()                      │
                     └─────────────────────────────────┘
```

## Class Dependencies

```
GameEngine
    │
    ├── HitstopManager          (juice.py)
    ├── KnockbackManager        (juice.py)
    ├── CameraTrauma            (juice.py)
    ├── BobbingCamera           (juice.py)
    ├── ScreenPulse             (juice.py)
    ├── FootstepTimer           (juice.py)
    ├── NumberTicker            (juice.py)
    │
    ├── ParticleSystem          (effects.py - existing)
    ├── RedVignette             (effects.py - NEW)
    ├── DustPuffEmitter         (effects.py - NEW)
    │
    └── Hero
        └── SquashStretch       (juice.py)

VerbBar
    │
    ├── hover_scales: Dict      (Verb → float)
    └── ease_out_cubic          (juice.py)

InventoryWindow
    │
    └── FloatingAnimation       (juice.py)

PauseMenu
    │
    └── SlideInAnimation        (juice.py)

Room
    │
    ├── FlickerLight[]          (effects.py - existing)
    ├── SmokeEmitter[]          (effects.py - NEW)
    ├── LightSpill[]            (effects.py - NEW)
    └── FlutteringPoster[]      (effects.py - NEW)
```

## Easing Curve Visualization

```
Linear (ease_linear)
    1.0 ┤                    ╱
        │                 ╱
        │              ╱
    0.5 ┤           ╱
        │        ╱
        │     ╱
    0.0 ┼──────────────────
        0.0              1.0

Ease Out Quad (ease_out_quad)
    1.0 ┤            ╭───────
        │         ╱
        │      ╱
    0.5 ┤    ╱
        │  ╱
        │╱
    0.0 ┼──────────────────
        0.0              1.0

Ease Out Bounce (ease_out_bounce)
    1.0 ┤      ╭╮  ╭──
        │     ╱ ╰╮╱
        │    ╱
    0.5 ┤  ╱
        │ ╱
        │╱
    0.0 ┼──────────────────
        0.0              1.0

Ease Out Elastic (ease_out_elastic)
    1.2 ┤    ╭╮╭──────
    1.0 ┤   ╱╰╯
        │  ╱
    0.5 ┤ ╱
        │╱
    0.0 ┼──────────────────
        0.0              1.0
```

## Performance Budget

```
┌─────────────────────┬──────────────┬─────────────┐
│ System              │ Update Cost  │ Draw Cost   │
├─────────────────────┼──────────────┼─────────────┤
│ HitstopManager      │ ~0.01ms      │ 0ms         │
│ KnockbackManager    │ ~0.02ms      │ 0ms         │
│ CameraTrauma        │ ~0.05ms      │ 0ms         │
│ SquashStretch       │ ~0.02ms      │ ~0.1ms      │
│ ParticleSystem      │ ~0.3ms       │ ~0.5ms      │
│ DustPuffEmitter     │ ~0.1ms       │ ~0.2ms      │
│ RedVignette         │ ~0.05ms      │ ~0.8ms *    │
│ Environmental FX    │ ~0.2ms       │ ~0.4ms      │
│ UI Animations       │ ~0.05ms      │ ~0.1ms      │
├─────────────────────┼──────────────┼─────────────┤
│ TOTAL               │ ~0.8ms       │ ~2.1ms      │
└─────────────────────┴──────────────┴─────────────┘

* RedVignette is pre-rendered if possible

Target: 60fps = 16.67ms per frame
Juice overhead: ~2.9ms = 17% of frame budget
Remaining: ~13.77ms for game logic
```

## State Machine Integration

```
GameState.PLAYING
    │
    ├─── Hitstop active?
    │    │
    │    ├──YES──► Skip gameplay updates
    │    │         Update only visual effects
    │    │         Return early
    │    │
    │    └──NO───► Continue normal updates
    │
    └─── Normal update flow
         │
         ├──► Update juice systems
         ├──► Update characters (with knockback)
         ├──► Update room/zombies
         └──► Update UI

GameState.PAUSED
    │
    └──► Update visual effects only
         (glow, particles, transitions)
         Skip gameplay updates

GameState.DIALOGUE
    │
    └──► Update visual effects only
         Skip gameplay updates
```

## Recommended Integration Order

```
Phase 1: Core Combat (30 minutes)
    1. Add juice.py imports to engine.py
    2. Initialize juice managers in __init__()
    3. Enhance _damage_hero() with hitstop/knockback
    4. Test: Take damage → should freeze and push back

Phase 2: Camera Feel (15 minutes)
    5. Add camera trauma to draw()
    6. Add camera bob to draw()
    7. Test: Damage shakes screen, walking bobs camera

Phase 3: Movement Polish (20 minutes)
    8. Add squash/stretch to Hero
    9. Add footstep dust emitter
    10. Test: Walking feels more alive

Phase 4: UI Juice (15 minutes)
    11. Add hover scaling to VerbBar
    12. Add health number ticker
    13. Test: UI feels responsive

Phase 5: Environmental (20 minutes)
    14. Add environmental effects to rooms
    15. Add red vignette to zombie groans
    16. Test: World feels alive

Total: ~100 minutes for complete integration
```

## File Structure Summary

```
zombie_quest/
│
├── juice.py                        ← NEW: 570 lines
│   ├── Easing functions           (12 curves)
│   ├── HitstopManager             (Combat)
│   ├── KnockbackManager           (Combat)
│   ├── FlashEffect                (Combat)
│   ├── CameraTrauma               (Camera)
│   ├── BobbingCamera              (Camera)
│   ├── SquashStretch              (Movement)
│   ├── FootstepTimer              (Movement)
│   ├── NumberTicker               (UI)
│   ├── FloatingAnimation          (UI)
│   ├── SlideInAnimation           (UI)
│   ├── BounceAnimation            (UI)
│   ├── ScreenPulse                (Audio-Visual)
│   └── AttentionPulse             (Attention)
│
├── effects.py                      ← ENHANCED: +350 lines
│   ├── [Existing effects...]
│   ├── FlutteringPoster           ← NEW
│   ├── SmokeEmitter/SmokeWisp     ← NEW
│   ├── RedVignette                ← NEW
│   ├── DustPuffEmitter/DustPuff   ← NEW
│   └── LightSpill                 ← NEW
│
├── engine.py                       ← INTEGRATION REQUIRED
├── characters.py                   ← INTEGRATION REQUIRED
└── ui.py                           ← INTEGRATION REQUIRED
```

## Quick Reference: What Goes Where

```
engine.py:
    __init__():     Initialize all juice managers
    update():       Check hitstop, apply knockback, emit dust
    _damage_hero(): Trigger hitstop + knockback + trauma
    _update_room(): Trigger red vignette on groan
    draw():         Apply camera trauma + bob

characters.py:
    Hero.__init__():  Add SquashStretch
    Hero.draw():      Apply squash/stretch scales
    Zombie.__init__(): Add FlashEffect (optional)
    Zombie.draw():     Apply flash (optional)

ui.py:
    VerbBar.__init__():        Add hover scales
    VerbBar.update():          Update hover animations
    VerbBar.draw():            Draw with scales
    InventoryWindow.__init__(): Add FloatingAnimation
    InventoryWindow.update():   Update float
    InventoryWindow.draw():     Apply float to selected
    PauseMenu.__init__():       Add SlideInAnimation
    PauseMenu.draw():           Draw with slide offsets
```

## Key Relationships

```
Trauma Decay:
    trauma(t) = initial_trauma - (decay_rate * t)
    shake(t) = trauma(t)² * max_offset * sin(time * speed)

Knockback Physics:
    offset(t) = direction * strength * (1 - easing(t/duration))

Squash/Stretch:
    scale_x = 1.0 ± deform
    scale_y = 1.0 ∓ deform  (inverse of x)
    volume preserved: scale_x * scale_y ≈ 1.0

Hover Animation:
    current += (target - current) * speed * dt
    (Smooth interpolation to target)
```

## Debug Visualization

To visualize juice systems, add debug overlay:

```python
def draw_debug(self, surface):
    """Draw debug info for juice systems."""
    font = pygame.font.Font(None, 20)
    y = 10

    # Hitstop
    text = font.render(f"Hitstop: {self.hitstop.frozen}", True, (255, 255, 255))
    surface.blit(text, (10, y))
    y += 20

    # Trauma
    trauma = self.camera_trauma.get_trauma()
    text = font.render(f"Trauma: {trauma:.2f}", True, (255, 255, 255))
    surface.blit(text, (10, y))
    y += 20

    # Knockback
    has_knockback = self.hero_knockback.active_knockback is not None
    text = font.render(f"Knockback: {has_knockback}", True, (255, 255, 255))
    surface.blit(text, (10, y))
    y += 20

    # Health ticker
    text = font.render(f"Health: {self.health_ticker.current:.1f} → {self.health_ticker.target}", True, (255, 255, 255))
    surface.blit(text, (10, y))
```

---

**This architecture enables professional-grade game feel with minimal performance overhead.**

All systems work together to create a cohesive, satisfying player experience. 🎮✨
