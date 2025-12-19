# Music Systems Quick Reference

## For Players: How to Use Music to Survive

### Musical Items

#### Guitar Pick
- **Music Type**: Guitar
- **Best Against**: Rocker Zombies (2x effective), Bouncer Zombies (1.6x)
- **Effect Radius**: Medium (120 pixels)
- **Duration**: 6 seconds
- **Strategy**: Use when rockers are nearby, they'll LOVE it

#### Demo Tape
- **Music Type**: New Wave
- **Best Against**: Scene Zombies (1.5x effective), DJ Zombies (1.4x)
- **Effect Radius**: Medium (100 pixels)
- **Duration**: 8 seconds
- **Strategy**: Perfect for hipster scene kids, they'll remember the good times

#### Setlist
- **Music Type**: Ambient
- **Best Against**: DJ Zombies (1.5x), Scene Zombies (1.2x)
- **Effect Radius**: Large (140 pixels)
- **Duration**: 10 seconds
- **Strategy**: Longest effect, calms multiple zombies at once

#### Vinyl Record
- **Music Type**: Punk
- **Best Against**: Bouncer Zombies (1.8x), Rocker Zombies (1.7x)
- **Effect Radius**: Large (130 pixels)
- **Duration**: 12 seconds
- **Strategy**: Most powerful and longest-lasting, use wisely

### Zombie Music Preferences Cheat Sheet

```
┌─────────────┬──────────┬────────┬──────────┬───────┬─────────┐
│ Zombie Type │ New Wave │ Electr │  Guitar  │ Punk  │ Ambient │
├─────────────┼──────────┼────────┼──────────┼───────┼─────────┤
│ Scene       │  ★★★★★   │  ★★★★  │   ★★★    │  ★★★★ │  ★★★★   │
│ Bouncer     │   ★★     │   ★★   │  ★★★★★   │ ★★★★★ │   ★     │
│ Rocker      │   ★★★    │   ★★   │  ★★★★★★  │ ★★★★★ │   ★★    │
│ DJ          │  ★★★★    │ ★★★★★★ │   ★★     │  ★★★  │  ★★★★★  │
└─────────────┴──────────┴────────┴──────────┴───────┴─────────┘

★★★★★★ = LOVES IT (Remembering state - backs away peacefully)
★★★★★  = Really likes (Dancing state - harmless swaying)
★★★★   = Likes (Dancing or Entranced)
★★★    = Neutral (Entranced - frozen)
★★     = Dislikes (minimal effect)
★      = Hates (may anger them)
```

### Room Audio Sources (Permanent)

#### Hennepin Outside (Street)
- Record Store Door: Punk music (weak)
- KJRR Alley: Electronic static (weak)
- **Strategy**: Not much musical advantage here, prepare your items

#### Let It Be Records
- Listening Booth: New Wave vinyl (STRONG)
- Store Speakers: Ambient synth (medium)
- **Strategy**: Scene zombies naturally pacified here, use Guitar Pick for rockers

#### KJRR College Station
- Broadcast Booth: Electronic (VERY STRONG)
- Record Library: New Wave (weak)
- **Strategy**: DJ zombie heaven, they'll be entranced by the broadcast

#### Backstage
- Stage Area: Guitar practice (strong)
- Equipment: Punk soundcheck (medium)
- **Strategy**: Rockers and bouncers are vulnerable here

#### Green Room
- Room Center: Acoustic tuning (medium)
- Boombox: New Wave cassette (weak)
- **Strategy**: Calm atmosphere helps with all zombie types

### Combat Tips

1. **Check Zombie Types First**: Look at what zombies are in the room before using items
2. **Position Matters**: Get within radius (120-140 pixels) of zombies
3. **Stack Effects**: Room sources + item = maximum effect
4. **Save Vinyl**: Most powerful, use on tough situations
5. **Watch Duration**: Effects last 6-12 seconds, plan your escape
6. **Music Tension**: When music calms down, you've pacified all threats

### Visual Feedback
- **Cyan Sparkles**: Zombie is affected by music
- **Message**: Shows how many zombies reacted
- **Music Changes**: Background music indicates safety level
- **Zombie Behavior**:
  - Standing still = Entranced
  - Gentle swaying = Dancing
  - Backing away = Remembering

---

## For Developers: Technical Reference

### Adding New Musical Items

```python
# In diegetic_audio.py, add to item_configs dict:
'New Item Name': {
    'music_type': 'punk',        # or 'guitar', 'electronic', 'new_wave', 'ambient'
    'radius': 120.0,             # pixels
    'intensity': 0.8,            # 0.0-1.0
    'duration': 8.0,             # seconds
    'description': 'Item description'
}
```

### Adding New Music Types

1. Add to zombie affinity dicts in `characters.py`:
```python
'new_music_type': 1.5,  # multiplier
```

2. Add room layer in `audio.py`:
```python
self.music_layers.append(ProceduralMusicLayer(
    name="new_layer",
    base_freq=220,
    pattern=[0, 4, 7, 12],
    waveform="triangle",
    duration=8.0
))
```

3. Add to room volumes in `set_music_tension()`:
```python
room_volumes['new_layer'] = 0.4
```

### Adding Diegetic Sources to Rooms

In `diegetic_audio.py`, `_setup_room_sources()`:
```python
self.room_sources['room_id'] = [
    DiegeticSource(
        position=(x, y),
        music_type='electronic',
        radius=150.0,
        intensity=0.7,
        description="Source description"
    ),
]
```

### Music State Priority

States are evaluated by priority:
```python
HOSTILE = 0       # Lowest - can be overridden
ENTRANCED = 1     # Medium
DANCING = 2       # High
REMEMBERING = 3   # Highest - hardest to achieve
```

### Intensity Thresholds

```python
effective_intensity < 0.3  → HOSTILE
0.3 ≤ effective_intensity < 0.6  → ENTRANCED
0.6 ≤ effective_intensity < 0.9  → DANCING
effective_intensity ≥ 0.9  → REMEMBERING
```

### Testing Checklist

- [ ] Zombie responds to all music types
- [ ] Music state expires after duration
- [ ] Multiple sources stack correctly
- [ ] Room transition loads new sources
- [ ] Visual feedback appears
- [ ] Music tension updates
- [ ] Item works from inventory
- [ ] Message displays correctly

---

## Troubleshooting

### "No zombies are close enough to hear"
- **Cause**: Zombies outside item radius
- **Solution**: Move closer to zombies before using item

### Zombies still attacking after music
- **Cause**: Wrong music type for zombie
- **Solution**: Check zombie type and use appropriate item

### Music not affecting zombies
- **Cause**: Intensity too low (< 0.3 effective)
- **Solution**: Use item that zombie prefers, or get closer

### Multiple zombies, only some affected
- **Cause**: Some zombies outside radius
- **Solution**: Position between zombies, or use item with larger radius

### Music effect wore off too quickly
- **Cause**: Duration expired
- **Solution**: Use longer-duration items, or chain multiple items

---

## Achievement Ideas

🎵 **Maestro**: Pacify 10 zombies with music
🎸 **Rocker's Friend**: Make a rocker zombie dance
💿 **DJ's Choice**: Max out a DJ zombie with electronic
🎼 **Symphony of the Dead**: All zombies dancing simultaneously
🎹 **Perfect Harmony**: Complete room without attacking zombies
🎺 **One-Man Band**: Use all musical items in single room
🎻 **Music Therapist**: Achieve REMEMBERING state on 5 zombies

---

**Remember: In 1982 Minneapolis, music isn't just art—it's survival!**
