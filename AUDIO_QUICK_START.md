# Audio System Quick Start

## 🎵 What's New

Your zombie game now has a **professional atmospheric audio system** with:
- 30+ synthesized sound effects
- Procedural music that adapts to gameplay tension
- Spatial audio for zombie groans
- Room-specific ambient soundscapes
- Event-driven architecture

## 🎮 It Just Works

The audio system is **already integrated** into your game. Just run it:

```bash
./run_game.sh
```

You'll immediately hear:
- Room ambience when you enter different locations
- Spatially-positioned zombie groans
- Music that gets more intense as zombies chase you
- UI feedback sounds
- Combat and item sounds

## 🔊 Sound Inventory

### Zombies (All Types: scene, bouncer, rocker, dj)
Each zombie type has its own unique pitch range:
- **Scene Zombie**: Mid-range hipster groan
- **Bouncer Zombie**: Deep threatening groan
- **Rocker Zombie**: Higher raspy groan
- **DJ Zombie**: Modulated groan

### Rooms
Each room has unique ambience that plays automatically:
- **Hennepin Avenue**: Traffic, wind, distant sirens
- **Record Store**: Muffled bass, crowd murmur, vinyl crackle
- **Radio Station**: Electrical hum, equipment buzz, tape hiss
- **Backstage**: Equipment buzz, distant drums
- **Green Room**: HVAC, conversations, footsteps above

### Music System
5 procedural layers crossfade automatically:
- Calm exploration (bass + arpeggio)
- Zombie nearby (pulse layer fades in)
- Being chased (lead layer at full volume)

## 🎹 Quick Code Examples

### Play a Sound
```python
from zombie_quest.audio import get_audio_manager

audio = get_audio_manager()
audio.play('zombie_groan_rocker', volume=0.5)
audio.play('pickup')
audio.play('success')
```

### Spatial Audio
```python
# Automatically plays from zombie's position
audio.play_spatial(
    'zombie_groan_bouncer',
    source_pos=(zombie_x, zombie_y),
    listener_pos=(hero_x, hero_y),
    volume=0.6
)
```

### Change Music Tension
```python
from zombie_quest.audio import TensionLevel

audio.set_music_tension(TensionLevel.CHASE)
audio.set_music_tension(TensionLevel.SAFE)
```

### Use Event System
```python
# Clean, decoupled way to trigger sounds
audio.event_system.trigger('item_pickup', {})
audio.event_system.trigger('room_enter', {'room_id': 'record_store'})
```

## 🎛️ Volume Control

Adjust volumes at runtime:
```python
audio.set_master_volume(0.8)      # Overall volume
audio.set_music_volume(0.6)       # Music layers
audio.set_sfx_volume(0.8)         # Sound effects
audio.set_ambient_volume(0.4)     # Room ambience
```

## 🔧 Sound List Reference

### Movement
- `footstep`, `footstep_concrete`, `footstep_carpet`

### Items
- `pickup` - Sparkly arpeggio
- `item_use` - Two-tone success
- `item_error` - Dissonant failure

### Doors
- `door` - Standard transition
- `door_creak` - Old creaky door
- `door_slam` - Sharp impact

### Combat
- `hit` - Player damage
- `death` - Dramatic game over
- `health_low` - Warning beep

### Zombies (per type)
- `zombie_groan_{type}`
- `zombie_alert_{type}`
- `zombie_attack_{type}`

### UI
- `ui_click`, `ui_select`, `ui_back`, `ui_error`
- `message`, `success`, `error`

### Environment
- `electric_hum`, `neon_flicker`
- `vinyl_crackle`, `tape_hiss`

## 🎨 The 1982 Minneapolis Sound

The audio captures the era through:
- **Lo-fi 22kHz synthesis** (authentic 8-bit texture)
- **60Hz electrical hum** (North American AC frequency)
- **Analog tape artifacts** (hiss, warmth, crackle)
- **Punk/new wave aesthetics** (square waves, minor keys, distortion)
- **Club atmosphere** (muffled bass, crowd murmur, distant drums)
- **Urban ambience** (traffic, sirens, wind)

## 📚 Full Documentation

See `AUDIO_SYSTEM.md` for:
- Complete technical details
- Synthesis algorithms
- Customization guide
- Performance tuning
- How to add your own sounds

## 🎼 Music Tension Auto-Adjustment

The engine automatically changes music based on zombie proximity:

| Distance | Chasing | Music State |
|----------|---------|-------------|
| < 50px   | Yes     | CHASE (full intensity) |
| < 100px  | Any     | DANGER (pulse layer) |
| < 150px  | No      | EXPLORATION (normal) |
| > 150px  | No      | SAFE (minimal) |

## 🎯 Zero Configuration Required

Everything is **already wired up**:
- ✅ Room ambience switches automatically
- ✅ Zombie groans use spatial positioning
- ✅ Music tension adjusts to gameplay
- ✅ Combat sounds trigger on damage
- ✅ UI sounds on interactions

Just play and enjoy the atmosphere!

---

**Rock on through the zombie apocalypse with genuine 1982 Minneapolis vibes.**
