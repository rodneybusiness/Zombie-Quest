## UX Enhancement Integration Guide

This guide shows how to integrate all the new UX systems into your game engine.

## Quick Start (Copy-Paste Ready)

### 1. Enhanced Movement System

Replace the Hero import in `engine.py`:

```python
# OLD
from .characters import Hero, ZombieSpawner

# NEW
from .characters_enhanced import EnhancedHero as Hero, ZombieSpawner
```

That's it! The enhanced movement is now active with:
- Smooth acceleration (0-max speed in 0.15s)
- Deceleration/momentum (slide to stop in 0.1s)
- 8-direction facing
- Keyboard interrupts pathfinding automatically

### 2. Hotspot Highlighting

Add to `engine.py` imports:

```python
from .hotspot_highlight import HotspotHighlighter
```

In `GameEngine.__init__()`:

```python
# Hotspot highlighting
self.hotspot_highlighter = HotspotHighlighter()
```

In `GameEngine.handle_events()`, update hover detection:

```python
def handle_events(self) -> None:
    mouse_pos = pygame.mouse.get_pos()
    room_pos = self.screen_to_room(mouse_pos)

    # Update hotspot highlight
    if room_pos:
        hotspot = self.current_room.find_hotspot((int(room_pos[0]), int(room_pos[1])))
        self.hotspot_highlighter.set_hotspot(hotspot)
    else:
        self.hotspot_highlighter.set_hotspot(None)

    # ... rest of event handling
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    self.hotspot_highlighter.update(dt)
    # ... rest of update
```

In `GameEngine.draw()`, after drawing the room:

```python
def draw(self) -> None:
    # ... draw room
    self.screen.blit(self.room_surface, (shake_x, UI_BAR_HEIGHT + shake_y))

    # Draw hotspot highlights
    self.hotspot_highlighter.draw_highlight(
        self.screen,
        room_offset=(shake_x, UI_BAR_HEIGHT + shake_y)
    )

    # Draw cursor icon
    mouse_pos = pygame.mouse.get_pos()
    self.hotspot_highlighter.draw_cursor_icon(
        self.screen,
        mouse_pos,
        self.verb_bar.selected_verb
    )

    # ... rest of draw
```

### 3. Radial Context Menu

Add to `engine.py` imports:

```python
from .radial_menu import ContextMenuManager
```

In `GameEngine.__init__()`:

```python
# Radial menu (can toggle on/off)
self.radial_menu = ContextMenuManager()
self.radial_menu.enabled = True  # Set False to use traditional verb bar
```

In `GameEngine._handle_mouse_click()`:

```python
def _handle_mouse_click(self, event: pygame.event.Event) -> None:
    if event.button == 3:  # Right click
        # Open radial menu
        room_pos = self.screen_to_room(event.pos)
        if room_pos:
            hotspot = self.current_room.find_hotspot((int(room_pos[0]), int(room_pos[1])))
            self.radial_menu.open_at_cursor(event.pos, hotspot)
            self.audio.play("ui_click")
        return

    if event.button == 1:  # Left click
        # Check if clicking radial menu
        selected_verb = self.radial_menu.handle_click(event.pos)
        if selected_verb:
            self.verb_bar.selected_verb = selected_verb
            self.audio.play("ui_select")
            return

        # ... rest of left click handling
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    mouse_pos = pygame.mouse.get_pos()
    self.radial_menu.update(dt, mouse_pos)
    # ... rest of update
```

In `GameEngine.draw()`:

```python
def draw(self) -> None:
    # ... draw everything else

    # Draw radial menu on top
    self.radial_menu.draw(self.screen)

    # ... rest of draw
```

### 4. Enhanced Inventory

Replace inventory window in `engine.py` imports:

```python
# OLD
from .ui import InventoryWindow

# NEW
from .inventory_enhanced import EnhancedInventoryWindow
```

In `GameEngine.__init__()`:

```python
# Enhanced inventory
self.inventory_window = EnhancedInventoryWindow(
    self.inventory,
    pygame.Rect(40, UI_BAR_HEIGHT + 20, WINDOW_SIZE[0] - 80, 140),
)
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    mouse_pos = pygame.mouse.get_pos()
    if self.inventory_window.visible:
        self.inventory_window.update(dt, mouse_pos)
    # ... rest of update
```

In `GameEngine._handle_mouse_click()`:

```python
def _handle_mouse_click(self, event: pygame.event.Event) -> None:
    if event.button == 1:  # Left click
        # Handle inventory mouse down
        if self.inventory_window.visible:
            self.inventory_window.handle_mouse_down(event)
            return
        # ... rest of click handling
```

Add mouse up handler in `GameEngine._handle_playing_event()`:

```python
def _handle_playing_event(self, event: pygame.event.Event) -> None:
    # ... existing key handling

    elif event.type == pygame.MOUSEBUTTONUP:
        if self.inventory_window.visible:
            result = self.inventory_window.handle_mouse_up(event)
            if result:
                action, item = result
                if action == "use":
                    self.message_box.show(f"Using {item.name}...")
                    self.audio.play("ui_select")
            return
```

Show full feedback when inventory is full:

```python
def give_item_to_inventory(self, item_name: str) -> None:
    item = self.items_catalog.get(item_name)
    if item:
        if not self.inventory.add_item(item):
            # Inventory full!
            self.inventory_window.show_full_message()
            self.message_box.show("Your flight case is full!")
            self.audio.play("error")
        else:
            # Success
            self.message_box.show(f"You stash the {item.name} in your flight case.")
            self.audio.play("pickup")
            # ... particle effects
```

### 5. Accessibility System

Add to `engine.py` imports:

```python
from .accessibility import AccessibilityConfig, SubtitleSystem, AccessibilityMenu, ColorblindPalette
```

In `GameEngine.__init__()`:

```python
# Accessibility
self.accessibility_config = AccessibilityConfig()
self.subtitles = SubtitleSystem(enabled=self.accessibility_config.subtitles_enabled)
self.accessibility_menu = AccessibilityMenu(
    self.accessibility_config,
    pygame.Rect(WINDOW_SIZE[0] // 2 - 200, WINDOW_SIZE[1] // 2 - 200, 400, 400)
)
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    # Update subtitles
    self.subtitles.update(dt)
    # ... rest of update
```

In `GameEngine.draw()`:

```python
def draw(self) -> None:
    # ... draw everything else

    # Draw subtitles
    self.subtitles.draw(self.screen, self.accessibility_config)

    # Draw accessibility menu if open
    if self.accessibility_menu.visible:
        self.accessibility_menu.draw(self.screen)
```

Add subtitle triggers throughout your code:

```python
# Example: Audio cues
self.audio.play("zombie_groan")
self.subtitles.add_subtitle("*Zombie groans nearby*", duration=1.5, color=(150, 150, 150))

# Example: Dialogue
self.subtitles.add_subtitle(dialogue_text, duration=3.0, speaker="DJ")

# Example: Important events
self.subtitles.add_subtitle("You hear footsteps behind you...", duration=2.0, color=COLORS.HOT_MAGENTA)
```

Apply colorblind palette:

```python
# In your drawing code, adjust colors based on mode
if self.accessibility_config.colorblind_mode != ColorblindMode.NONE:
    adjusted_color = ColorblindPalette.adjust_color(original_color, self.accessibility_config.colorblind_mode)
else:
    adjusted_color = original_color
```

Apply screen shake intensity:

```python
# In your screen shake code
shake_intensity = base_intensity * self.accessibility_config.screen_shake_intensity
if not self.accessibility_config.screen_shake_enabled:
    shake_intensity = 0

self.screen_shake.shake(shake_intensity, duration)
```

### 6. Tutorial System

Add to `engine.py` imports:

```python
from .tutorial import TutorialSystem, TutorialHint, ObjectHighlighter
```

In `GameEngine.__init__()`:

```python
# Tutorial
self.tutorial = TutorialSystem(enabled=True)
self.object_highlighter = ObjectHighlighter()

# Show first tutorial hints
self.tutorial.show_hint(TutorialHint.MOVEMENT_WASD)
```

Add tutorial triggers:

```python
# When player moves
def update(self, dt: float) -> None:
    # ... after hero update
    if self.hero.movement.is_moving():
        self.tutorial.on_player_moved()
    # ... rest

# When player interacts
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
    self.tutorial.on_player_interacted()
    # ... rest

# When inventory opens
def _handle_keydown(self, event: pygame.event.Event) -> None:
    if key == pygame.K_i:
        self.inventory_window.toggle()
        if self.inventory_window.visible:
            self.tutorial.on_inventory_opened()
        # ...

# When zombie gets close
def _update_room(self, dt: float) -> None:
    for zombie in self.current_room.zombies:
        collision = zombie.update(dt, hero_pos, room_rect)

        # Check distance for tutorial
        if zombie.is_chasing:
            self.tutorial.on_zombie_nearby()
        # ...

# When health is low
def _damage_hero(self, amount: int) -> None:
    if self.hero.take_damage(amount):
        # ... death
    else:
        # Check low health
        if self.hero.health <= 1:
            self.tutorial.on_health_low()
        # ...
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    self.tutorial.update(dt)
    self.object_highlighter.update(dt)
    # ... rest
```

In `GameEngine.draw()`:

```python
def draw(self) -> None:
    # ... draw room

    # Draw object highlights (before UI)
    self.object_highlighter.draw(
        self.screen,
        room_offset=(shake_x, UI_BAR_HEIGHT + shake_y)
    )

    # ... draw UI

    # Draw tutorial hints (on top of everything)
    self.tutorial.draw(self.screen)
```

Highlight first interactable object:

```python
# In room setup or first frame
if self.current_room.hotspots and not self.tutorial.first_interaction:
    first_hotspot = self.current_room.hotspots[0]
    self.object_highlighter.highlight_object(first_hotspot.rect)
    self.tutorial.show_hint(TutorialHint.INTERACT_HOTSPOT)
```

### 7. Feedback Juice Effects

Add to `engine.py` imports:

```python
from .feedback_juice import FeedbackJuice
```

In `GameEngine.__init__()`:

```python
# Feedback juice
self.juice = FeedbackJuice()
```

In `GameEngine.update()`:

```python
def update(self, dt: float) -> None:
    # Let juice modify dt (for freeze frames)
    actual_dt = self.juice.update(dt)

    # Use actual_dt for game updates
    self.hero.update(actual_dt, ...)
    # ... rest of updates using actual_dt
```

In `GameEngine.draw()`:

```python
def draw(self) -> None:
    # ... draw everything

    # Apply zoom pulse to camera (if desired)
    zoom = self.juice.get_zoom_scale()
    if zoom != 1.0:
        # Scale the room surface before blitting
        scaled_width = int(ROOM_WIDTH * zoom)
        scaled_height = int(ROOM_HEIGHT * zoom)
        scaled_room = pygame.transform.scale(self.room_surface, (scaled_width, scaled_height))

        # Center the scaled room
        offset_x = (ROOM_WIDTH - scaled_width) // 2 + shake_x
        offset_y = (ROOM_HEIGHT - scaled_height) // 2 + shake_y
        self.screen.blit(scaled_room, (offset_x, UI_BAR_HEIGHT + offset_y))
    else:
        self.screen.blit(self.room_surface, (shake_x, UI_BAR_HEIGHT + shake_y))

    # ... draw UI

    # Draw juice effects (vignette, flash, letterbox)
    self.juice.draw(self.screen)
```

Trigger juice effects:

```python
# Item pickup
def give_item_to_inventory(self, item_name: str) -> None:
    if self.inventory.add_item(item):
        self.juice.item_pickup()  # Zoom pulse + flash
        # ...

# Damage taken
def _damage_hero(self, amount: int) -> None:
    if self.hero.take_damage(amount):
        # ... death
    else:
        self.juice.damage_taken(intensity=0.6)  # Vignette + freeze + aberration
        # ...

# Room transitions
def change_room(self, room_id: str, ...) -> None:
    self.juice.room_transition_start()  # Letterbox in

    def do_transition():
        # ... actually change room
        self.juice.room_transition_end()  # Letterbox out

    self.transition.start_transition(halfway_callback=do_transition)
    # ...

# Success moments
def perform_hotspot_action(self, hotspot: Hotspot, verb: Verb) -> None:
    # ... check outcome
    if interaction_outcome == "success":
        self.juice.success_moment(color=COLORS.NEON_GOLD)
    # ...

# Heavy impacts
if zombie_hit_hero:
    self.juice.impact_hit()  # Freeze + chromatic aberration
```

## Configuration

### Toggle Features On/Off

All systems can be enabled/disabled:

```python
# In GameEngine.__init__() or settings
self.radial_menu.enabled = False  # Use traditional verb bar
self.tutorial.enabled = False  # Disable tutorial hints
self.accessibility_config.subtitles_enabled = False
self.accessibility_config.reduced_motion = True  # Less screen shake/effects
```

### Customize Movement Feel

```python
# In characters_enhanced.py, modify MovementConfig:
movement_config = MovementConfig(
    max_speed=100.0,  # Faster movement
    acceleration_time=0.08,  # Snappier acceleration
    deceleration_time=0.15,  # More sliding
)
```

### Customize Tutorial Hints

```python
# Modify hints in tutorial.py
TutorialSystem.HINTS[TutorialHint.MOVEMENT_WASD] = HintConfig(
    text="Your custom hint text here",
    duration=6.0,
    position="center"
)
```

## Testing Checklist

After integration, test:

- [ ] Movement feels smooth with acceleration/deceleration
- [ ] Keyboard interrupts pathfinding cleanly
- [ ] Hotspots highlight when mouse hovers
- [ ] Right-click opens radial menu with valid verbs
- [ ] Inventory shows tooltips on hover
- [ ] Drag items from inventory to use them
- [ ] "Inventory full" message shows when adding to full inventory
- [ ] Tutorial hints appear at appropriate times
- [ ] Subtitles show for audio events
- [ ] Item pickup triggers zoom pulse
- [ ] Taking damage shows red vignette and freeze frame
- [ ] Room transitions show letterbox effect
- [ ] Accessibility menu can be opened and settings work

## Performance Notes

All systems are designed to be performant:

- Hotspot highlighting: Only updates on mouse move
- Radial menu: Only draws when active
- Tutorial: Minimal overhead when hints not shown
- Juice effects: Efficient surface operations
- Enhanced movement: Simple vector math

If you experience slowdown, you can disable individual effects or reduce quality:

```python
# Reduce particle count
self.particles.emit_burst(x, y, color, count=5)  # Instead of 10

# Disable chromatic aberration (most expensive)
# Don't call juice.chromatic methods

# Reduce subtitle update frequency
if frame_count % 2 == 0:  # Only update every other frame
    self.subtitles.update(dt * 2)
```

## Troubleshooting

### Movement feels weird
- Check that `actual_dt` from juice.update() is being used
- Verify acceleration/deceleration times aren't too extreme
- Make sure keyboard input isn't being double-processed

### Radial menu doesn't show
- Verify `radial_menu.enabled = True`
- Check that right-click events aren't being consumed elsewhere
- Ensure radial menu is drawn last (on top of everything)

### Tutorial hints don't appear
- Check `tutorial.enabled = True`
- Verify hint triggers are being called
- Make sure tutorial.draw() is called after other UI

### Accessibility features don't work
- Ensure config is being passed to relevant systems
- Check that colorblind adjustments are applied to all color usage
- Verify subtitle system is receiving event triggers

## Advanced Integration

### Custom Feedback Effects

Create your own juice effects:

```python
# In your code
class MyCustomEffect:
    def __init__(self):
        self.active = False
        self.time = 0.0

    def trigger(self):
        self.active = True
        self.time = 0.0

    def update(self, dt):
        if self.active:
            self.time += dt
            if self.time > 1.0:
                self.active = False

    def draw(self, surface):
        if self.active:
            # Draw your effect
            pass

# Add to FeedbackJuice
self.juice.my_effect = MyCustomEffect()
```

### Extend Tutorial System

Add your own hints:

```python
# Add to TutorialHint enum in tutorial.py
class TutorialHint(Enum):
    # ... existing hints
    CUSTOM_HINT = "custom_hint"

# Add configuration
TutorialSystem.HINTS[TutorialHint.CUSTOM_HINT] = HintConfig(
    text="Your hint here",
    duration=4.0
)

# Trigger it
self.tutorial.show_hint(TutorialHint.CUSTOM_HINT)
```

## Complete Example

Here's a minimal integration showing all systems working together:

```python
# In engine.py
from .characters_enhanced import EnhancedHero as Hero
from .hotspot_highlight import HotspotHighlighter
from .radial_menu import ContextMenuManager
from .inventory_enhanced import EnhancedInventoryWindow
from .accessibility import AccessibilityConfig, SubtitleSystem
from .tutorial import TutorialSystem, TutorialHint
from .feedback_juice import FeedbackJuice

class GameEngine:
    def __init__(self, base_path: str) -> None:
        # ... existing setup

        # Initialize all UX systems
        self.hero = Hero(hero_start)
        self.hotspot_highlighter = HotspotHighlighter()
        self.radial_menu = ContextMenuManager()
        self.inventory_window = EnhancedInventoryWindow(self.inventory, inv_rect)
        self.accessibility_config = AccessibilityConfig()
        self.subtitles = SubtitleSystem()
        self.tutorial = TutorialSystem()
        self.juice = FeedbackJuice()

        # Initial tutorial
        self.tutorial.show_hint(TutorialHint.MOVEMENT_WASD)

    def update(self, dt: float) -> None:
        # Juice modifies dt
        actual_dt = self.juice.update(dt)

        # Update all systems
        mouse_pos = pygame.mouse.get_pos()
        self.hotspot_highlighter.update(actual_dt)
        self.radial_menu.update(actual_dt, mouse_pos)
        self.inventory_window.update(actual_dt, mouse_pos)
        self.subtitles.update(actual_dt)
        self.tutorial.update(actual_dt)

        # Game updates with actual_dt
        self.hero.update(actual_dt, ...)

    def draw(self) -> None:
        # Draw game
        # ...

        # Draw UX layers (order matters!)
        self.hotspot_highlighter.draw_highlight(self.screen, room_offset)
        self.hotspot_highlighter.draw_cursor_icon(self.screen, mouse_pos, verb)
        self.radial_menu.draw(self.screen)
        self.inventory_window.draw(self.screen, mouse_pos)
        self.juice.draw(self.screen)
        self.subtitles.draw(self.screen, self.accessibility_config)
        self.tutorial.draw(self.screen)
```

That's it! You now have Hollow Knight/Hades-quality UX in your game.
