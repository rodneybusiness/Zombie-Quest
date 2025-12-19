# UX Enhancements - Quick Reference Card

## 🎮 Core Integrations (Copy-Paste Ready)

### Imports Block
```python
# Add to zombie_quest/engine.py
from .characters_enhanced import EnhancedHero as Hero
from .hotspot_highlight import HotspotHighlighter
from .radial_menu import ContextMenuManager
from .inventory_enhanced import EnhancedInventoryWindow
from .accessibility import AccessibilityConfig, SubtitleSystem, AccessibilityMenu
from .tutorial import TutorialSystem, TutorialHint
from .feedback_juice import FeedbackJuice
```

### Initialization Block
```python
# In GameEngine.__init__()
# Enhanced systems
self.hero = Hero(hero_start)
self.hotspot_highlighter = HotspotHighlighter()
self.radial_menu = ContextMenuManager()
self.inventory_window = EnhancedInventoryWindow(self.inventory, inv_rect)
self.accessibility = AccessibilityConfig()
self.subtitles = SubtitleSystem()
self.tutorial = TutorialSystem()
self.juice = FeedbackJuice()
```

### Update Loop
```python
# In GameEngine.update()
def update(self, dt: float) -> None:
    # Freeze frames modify dt
    actual_dt = self.juice.update(dt)

    # Update UX systems
    mouse_pos = pygame.mouse.get_pos()
    self.hotspot_highlighter.update(actual_dt)
    self.radial_menu.update(actual_dt, mouse_pos)
    if self.inventory_window.visible:
        self.inventory_window.update(actual_dt, mouse_pos)
    self.subtitles.update(actual_dt)
    self.tutorial.update(actual_dt)

    # Use actual_dt for game updates
    self.hero.update(actual_dt, room_bounds, walkable_check)
```

### Render Loop
```python
# In GameEngine.draw()
def draw(self) -> None:
    # ... draw room and characters

    # UX layers (order matters!)
    self.hotspot_highlighter.draw_highlight(self.screen, room_offset)
    self.hotspot_highlighter.draw_cursor_icon(self.screen, mouse_pos, verb)

    # ... draw UI elements

    self.radial_menu.draw(self.screen)
    self.inventory_window.draw(self.screen, mouse_pos)
    self.juice.draw(self.screen)
    self.subtitles.draw(self.screen, self.accessibility)
    self.tutorial.draw(self.screen)
```

## 🎯 Common Triggers

### Movement Feel
```python
# Already works! Just use EnhancedHero
# Keyboard input automatically smooth with acceleration
keys = pygame.key.get_pressed()
self.hero.handle_keyboard_input(keys)
```

### Hotspot Highlighting
```python
# In handle_events()
mouse_pos = pygame.mouse.get_pos()
room_pos = self.screen_to_room(mouse_pos)
if room_pos:
    hotspot = self.current_room.find_hotspot(room_pos)
    self.hotspot_highlighter.set_hotspot(hotspot)
```

### Radial Menu
```python
# Right-click to open
if event.button == 3:
    hotspot = self.current_room.find_hotspot(room_pos)
    self.radial_menu.open_at_cursor(event.pos, hotspot)

# Left-click to select
if event.button == 1:
    verb = self.radial_menu.handle_click(event.pos)
    if verb:
        self.verb_bar.selected_verb = verb
```

### Inventory
```python
# Handle mouse events
if event.type == pygame.MOUSEBUTTONDOWN:
    self.inventory_window.handle_mouse_down(event)
elif event.type == pygame.MOUSEBUTTONUP:
    result = self.inventory_window.handle_mouse_up(event)
    if result:
        action, item = result
        if action == "use":
            # Use the item!
            pass

# Show full message
if not self.inventory.add_item(item):
    self.inventory_window.show_full_message()
```

### Subtitles
```python
# Audio event
self.audio.play("zombie_groan")
self.subtitles.add_subtitle("*Zombie groans*", duration=1.5, color=(150,150,150))

# Dialogue
self.subtitles.add_subtitle(text, duration=3.0, speaker="DJ")

# Important event
self.subtitles.add_subtitle("You hear footsteps...", color=COLORS.HOT_MAGENTA)
```

### Tutorial
```python
# Show hints
self.tutorial.show_hint(TutorialHint.MOVEMENT_WASD)
self.tutorial.show_hint(TutorialHint.INTERACT_HOTSPOT)

# Trigger events
self.tutorial.on_player_moved()
self.tutorial.on_player_interacted()
self.tutorial.on_inventory_opened()
self.tutorial.on_zombie_nearby()
self.tutorial.on_health_low()
```

### Feedback Juice
```python
# Item pickup
self.juice.item_pickup()

# Damage
self.juice.damage_taken(intensity=0.6)

# Room transition
self.juice.room_transition_start()
# ... change room
self.juice.room_transition_end()

# Success
self.juice.success_moment(color=COLORS.NEON_GOLD)

# Impact
self.juice.impact_hit()
```

## ⚙️ Configuration Snippets

### Tweak Movement Feel
```python
# In characters_enhanced.py, modify EnhancedHero.__init__()
movement_config = MovementConfig(
    max_speed=100.0,           # Faster
    acceleration_time=0.08,    # Snappier
    deceleration_time=0.15     # More slide
)
```

### Customize Colors
```python
# In accessibility.py or your drawing code
if self.accessibility.colorblind_mode != ColorblindMode.NONE:
    color = ColorblindPalette.adjust_color(color, self.accessibility.colorblind_mode)
```

### Adjust Juice Intensity
```python
# More dramatic effects
self.juice.zoom_pulse.intensity = 0.1  # 10% zoom
self.juice.zoom_pulse.duration = 0.3   # Longer

# Disable specific effects
self.juice.freeze_frame.active = False
```

### Tutorial Customization
```python
# Change hint text
TutorialSystem.HINTS[TutorialHint.MOVEMENT_WASD].text = "Your custom text"
TutorialSystem.HINTS[TutorialHint.MOVEMENT_WASD].duration = 6.0

# Disable tutorial
self.tutorial.enabled = False
```

## 🎨 Visual Polish Tips

### Smooth Transitions
```python
# Always use easing for values
progress = self.time / self.duration
eased = progress ** 2  # Ease in
eased = 1 - (1 - progress) ** 2  # Ease out
```

### Pulsing Glows
```python
pulse = (math.sin(time * speed) + 1) / 2  # 0.0 to 1.0
intensity = min_value + pulse * (max_value - min_value)
```

### Fade Effects
```python
# Fade in
self.alpha = min(255, self.alpha + fade_speed * dt)

# Fade out
self.alpha = max(0, self.alpha - fade_speed * dt)
```

## 🔍 Debug Helpers

### Enable Debug Visualization
```python
# Show interaction radius (in accessibility.py)
self.interaction_radius = InteractionRadius(enabled=True)
self.interaction_radius.draw(surface, hotspots, room_offset)

# Show all tutorial hints
for hint in TutorialHint:
    print(f"{hint.value}: {self.tutorial.HINTS[hint].text}")

# Log movement state
print(f"Velocity: {self.hero.movement.velocity}")
print(f"Facing: {self.hero.movement.get_cardinal_direction()}")
```

### Performance Monitoring
```python
import time

start = time.time()
self.juice.update(dt)
elapsed = (time.time() - start) * 1000
if elapsed > 16:  # More than 16ms (60fps target)
    print(f"Juice update slow: {elapsed}ms")
```

## 📱 Platform-Specific

### Gamepad Support (Future)
```python
# Add to radial menu
if joystick.get_axis(0) != 0 or joystick.get_axis(1) != 0:
    angle = math.atan2(joystick.get_axis(1), joystick.get_axis(0))
    # Select radial menu item at angle
```

### Touch Support (Future)
```python
# Drag inventory items
if event.type == pygame.FINGERDOWN:
    self.inventory_window.handle_touch_down(event.x, event.y)
elif event.type == pygame.FINGERUP:
    self.inventory_window.handle_touch_up(event.x, event.y)
```

## 🎯 Common Patterns

### Conditional Effects
```python
# Only if accessibility allows
if self.accessibility.screen_shake_enabled:
    shake_amount *= self.accessibility.screen_shake_intensity
    self.screen_shake.shake(shake_amount)

if self.accessibility.flash_effects_enabled:
    self.juice.success_flash.trigger()
```

### Chained Effects
```python
# Combo effect
def big_success(self):
    self.juice.success_moment()
    self.juice.zoom_pulse.trigger()
    self.particles.emit_burst(x, y, COLORS.NEON_GOLD, count=20)
    self.audio.play("success")
    self.subtitles.add_subtitle("SUCCESS!", duration=2.0)
```

### Delayed Actions
```python
# Wait for juice effect to complete
if self.juice.freeze_frame.is_active():
    return  # Don't update game logic during freeze

if self.juice.letterbox.is_visible():
    # Don't allow input during transition
    return
```

## 🚨 Troubleshooting Quick Fixes

### Movement feels stuttery
```python
# Make sure using actual_dt from juice
actual_dt = self.juice.update(dt)
self.hero.update(actual_dt, ...)  # Use actual_dt, not dt!
```

### Highlights don't show
```python
# Draw order matters - highlights after room, before UI
self.current_room.draw(surface, hero)
self.hotspot_highlighter.draw_highlight(surface, offset)  # Now!
self.verb_bar.draw(surface)
```

### Radial menu behind other UI
```python
# Draw radial menu LAST
# ... all other UI
self.radial_menu.draw(surface)  # Must be last!
```

### Tutorial hints spam
```python
# Check if already shown
if TutorialHint.MOVEMENT_WASD not in self.tutorial.shown_hints:
    self.tutorial.show_hint(TutorialHint.MOVEMENT_WASD)
```

## 💾 Save/Load Accessibility Settings

```python
# Save
settings = {
    'font_size': self.accessibility.font_size.value,
    'colorblind_mode': self.accessibility.colorblind_mode.value,
    'screen_shake': self.accessibility.screen_shake_intensity,
    'subtitles': self.accessibility.subtitles_enabled,
}
with open('settings.json', 'w') as f:
    json.dump(settings, f)

# Load
with open('settings.json', 'r') as f:
    settings = json.load(f)
self.accessibility.font_size = FontSize(settings['font_size'])
self.accessibility.colorblind_mode = ColorblindMode(settings['colorblind_mode'])
# ... etc
```

## 🎓 Remember

1. **actual_dt** from juice.update() for freeze frames
2. **Draw order** matters for overlays
3. **Update before draw** for all UX systems
4. **Trigger subtitles** with audio events
5. **Tutorial.on_X()** when events happen
6. **Juice.X()** for satisfying feedback

## ✨ The Golden Rule

**Every player action should have immediate, clear feedback.**

If you click, tap, or press something and nothing happens for even 0.1 seconds, it feels broken. These systems ensure everything feels responsive and satisfying.

---

**Quick Start:** Copy the Imports, Initialization, Update, and Render blocks above, then add triggers as needed. That's it!
