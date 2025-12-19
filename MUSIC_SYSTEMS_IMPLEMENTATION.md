# Music-Based Gameplay Systems Implementation

This document details the comprehensive music-based gameplay systems added to Zombie Quest, making audio integral to gameplay rather than just atmospheric.

## Overview

The implementation consists of four major components:
1. **Zombie Music Response System** - Zombies react to music based on type and preferences
2. **Diegetic Audio Sources** - Positioned audio sources that exist in the game world
3. **Music-Based Item Mechanics** - Musical items affect nearby zombies
4. **Room-Specific Music Themes** - Each location has unique audio atmosphere

---

## 1. Zombie Music Response System

### Location
`/home/user/Zombie-Quest/zombie_quest/characters.py`

### Features Implemented

#### ZombieMusicState Enum
```python
class ZombieMusicState(Enum):
    HOSTILE = "hostile"          # Normal behavior, attacks player
    ENTRANCED = "entranced"      # Frozen in place, listening to music
    DANCING = "dancing"          # Swaying rhythmically, harmless
    REMEMBERING = "remembering"  # Brief lucidity, may even help player
```

#### Music Affinity System
Each zombie type has unique music preferences:

- **Scene Zombies**: Love new wave (1.5x), electronic (1.3x), ambient (1.2x)
- **Bouncer Zombies**: Prefer punk (1.8x), guitar (1.6x), hate electronic (0.4x)
- **Rocker Zombies**: LOVE guitar (2.0x), punk (1.7x), dislike electronic (0.5x)
- **DJ Zombies**: Obsessed with electronic (2.0x), ambient (1.5x), new wave (1.4x)

#### Response Mechanism
```python
def respond_to_music(self, music_type: str, intensity: float) -> ZombieMusicState
```
- Calculates `effective_intensity = intensity × affinity`
- Returns appropriate state:
  - < 0.3: HOSTILE (no effect)
  - 0.3-0.6: ENTRANCED (frozen, 3s duration)
  - 0.6-0.9: DANCING (harmless swaying, 5s duration)
  - > 0.9: REMEMBERING (lucid, moves away, 4s duration)

#### Behavioral Changes
- **ENTRANCED**: Zombie freezes in place, stops chasing
- **DANCING**: Gentle swaying motion, won't attack
- **REMEMBERING**: Slowly moves away from player, contemplative
- **All non-HOSTILE states**: Zombies are harmless, quieter groans

---

## 2. Diegetic Audio Sources

### Location
`/home/user/Zombie-Quest/zombie_quest/diegetic_audio.py` (NEW FILE)

### DiegeticSource Class
```python
@dataclass
class DiegeticSource:
    position: Tuple[float, float]  # World coordinates
    music_type: str                # 'guitar', 'electronic', 'new_wave', etc.
    radius: float                  # Effect radius in pixels
    intensity: float               # Base intensity (0.0-1.0)
    duration: float                # -1 for permanent sources
    description: str               # Human-readable description
```

#### Intensity Calculation
- Uses linear falloff: `intensity × (1 - distance/radius)`
- Only affects targets within radius
- Multiple sources can overlap and stack

### Room-Specific Permanent Sources

#### Hennepin Outside (Street)
- Record Store Door: Punk music (radius 120, intensity 0.3)
- Alley to KJRR: Electronic static (radius 80, intensity 0.2)

#### Record Store
- Listening Booth: New wave vinyl (radius 150, intensity 0.6) - Joy Division
- Store Speakers: Ambient synth (radius 100, intensity 0.4)

#### KJRR College Station
- Broadcast Booth: Electronic set (radius 180, intensity 0.8) - POWERFUL
- Record Library: New wave (radius 90, intensity 0.3)

#### Backstage
- Stage Area: Guitar practice (radius 140, intensity 0.5)
- Equipment Area: Punk soundcheck (radius 100, intensity 0.4)

#### Green Room
- Room Center: Acoustic tuning (radius 120, intensity 0.5)
- Boombox Corner: New wave cassette (radius 80, intensity 0.3)

### Musical Item Sources
When players use musical items, they create temporary diegetic sources:

- **Guitar Pick**: Guitar type, radius 120, intensity 0.8, 6s duration
- **Demo Tape**: New wave, radius 100, intensity 0.7, 8s duration
- **Setlist**: Ambient, radius 140, intensity 0.6, 10s duration
- **Vinyl Record**: Punk, radius 130, intensity 0.9, 12s duration

---

## 3. Music-Based Item Mechanics

### Location
`/home/user/Zombie-Quest/zombie_quest/engine.py`

### Implementation

#### Item Usage Flow
1. Player uses musical item (USE verb with item selected)
2. `_use_musical_item()` creates temporary diegetic source at player position
3. System checks all zombies within source radius
4. Affected zombies get music applied via `apply_music_effect()`
5. Visual feedback: cyan sparkles around affected zombies
6. Message shows how many and which types of zombies were affected

#### Example Messages
```python
"You strum a powerful chord on the pick. 2 Rocker zombies react to the music!"
"The demo tape crackles to life with basement energy. 1 Scene zombie reacts to the music!"
"You hum the setlist melodies, note by note. But no zombies are close enough to hear."
```

#### Integration with Game Loop
```python
def _apply_music_to_zombies(self) -> None:
    """Called every frame to apply all active diegetic sources to zombies."""
    for zombie in self.current_room.zombies:
        music_effects = self.diegetic_audio.get_music_at_position(zombie_pos)
        for music_type, intensity in music_effects:
            zombie.apply_music_effect(music_type, intensity)
```

#### Music State Affects Tension
- If all zombies are harmless (entranced/dancing/remembering), music tension drops to SAFE
- Individual zombie threat assessment considers music state
- Groan volumes adjusted: dancing (0.3), remembering (0.2), hostile (0.5)

---

## 4. Room-Specific Music Themes

### Location
`/home/user/Zombie-Quest/zombie_quest/audio.py`

### Procedural Music Layers Added

#### Room-Specific Layers
1. **street_punk**: E2, punk rhythm, square wave (for Hennepin Outside)
2. **record_newwave**: A3, new wave progression, triangle wave (for Record Store)
3. **radio_electronic**: A4, electronic melody, sawtooth wave (for KJRR)
4. **backstage_guitar**: E3, rock progression, square wave (for Backstage)
5. **greenroom_ambient**: E4, gentle acoustic, triangle wave (for Green Room)

#### Universal Tension Layers
- **bass**: Foundation layer (all rooms)
- **pulse**: Danger/tension layer
- **lead**: Chase sequence layer

### Dynamic Music Mixing

#### Tension Level Integration
```python
def set_music_tension(self, tension: TensionLevel, room_id: Optional[str] = None)
```

Music now considers BOTH tension level AND current room:

**SAFE State**
- Room layer: 0.3-0.4 volume
- Bass: 0.2
- No tension layers

**EXPLORATION State**
- Room layer: 0.3-0.5 volume
- Bass: 0.3
- Pulse: 0.1 (slight unease)

**DANGER State**
- Room layer: 0.15-0.25 (reduced 50%)
- Bass: 0.4
- Pulse: 0.4
- Lead: 0.2

**CHASE State**
- Room layer: 0.06-0.1 (reduced 80%)
- Bass: 0.5
- Pulse: 0.6
- Lead: 0.5 (full intensity)

### Room Atmosphere Examples

#### Hennepin Outside
- Safe: Distant punk bass pulses (0.3), city rumble
- Danger: Punk fades (0.15), tension rises

#### Record Store
- Safe: Rich new wave arpeggios (0.4), vinyl crackle
- Danger: New wave retreats (0.2), anxiety builds

#### KJRR Station
- Safe: Soaring electronic synths (0.5), radio energy
- Chase: Synths barely audible (0.1), pure adrenaline

---

## Gameplay Impact

### Strategic Considerations

1. **Know Your Zombies**
   - Rocker zombies in record store? Use Guitar Pick for maximum effect
   - DJ zombies near radio station? Electronic sources work best
   - Bouncer zombies? Punk or guitar will pacify them

2. **Musical Item Management**
   - Each item has limited duration (6-12 seconds)
   - Items create area of effect - position matters
   - Can affect multiple zombies simultaneously
   - Different items for different zombie types

3. **Environmental Advantage**
   - Record store listening booth naturally entrances scene zombies
   - KJRR broadcast booth affects DJ zombies strongly
   - Use room's permanent sources strategically

4. **Tension Feedback**
   - Music adapts to threat level AND location
   - When all zombies pacified, music becomes peaceful
   - Audio cues inform player of danger status

### Example Scenario

**Situation**: Player in Record Store with 2 Scene Zombies and 1 Rocker Zombie

**Solution 1**: Use Demo Tape (new wave)
- Scene zombies: 0.7 × 1.5 = 1.05 effective → REMEMBERING (they back away)
- Rocker zombie: 0.7 × 0.7 = 0.49 → ENTRANCED (frozen but not fully pacified)

**Solution 2**: Use Guitar Pick (guitar)
- Scene zombies: 0.8 × 0.8 = 0.64 → DANCING (harmless)
- Rocker zombie: 0.8 × 2.0 = 1.6 (capped at 1.0) → REMEMBERING (backs away)

**Optimal**: Guitar Pick fully pacifies the dangerous rocker while keeping scene zombies harmless

---

## Technical Architecture

### Data Flow
```
Musical Item Used
    ↓
DiegeticSource Created (position, type, radius, intensity)
    ↓
Added to DiegeticAudioManager.sources[]
    ↓
Every Frame: _apply_music_to_zombies()
    ↓
For each zombie: get_music_at_position(zombie_pos)
    ↓
Returns [(music_type, intensity), ...] for all affecting sources
    ↓
zombie.apply_music_effect(music_type, intensity)
    ↓
Zombie calculates effective_intensity = intensity × affinity[type]
    ↓
Sets music_state based on effective_intensity
    ↓
Zombie.update() uses music_state to modify behavior
    ↓
Music tension system checks zombie.is_harmless()
    ↓
Audio manager adjusts music layers for room + tension
```

### File Structure
```
zombie_quest/
├── characters.py       [MODIFIED] - Zombie music response system
├── diegetic_audio.py   [NEW]      - Positioned audio sources
├── engine.py           [MODIFIED] - Music mechanics integration
└── audio.py            [MODIFIED] - Room-specific music themes
```

---

## Period-Authentic Integration

All music systems respect the 1982 Minneapolis punk/new wave aesthetic:

### Music Types
- **Punk**: Raw, aggressive, anti-establishment (Hüsker Dü, The Replacements)
- **New Wave**: Synthesized, danceable, experimental (Prince, The Suburbs)
- **Guitar**: Rock energy, live instruments (First Avenue scene)
- **Electronic**: Synth-driven, radio-friendly (college radio era)
- **Ambient**: Atmospheric, introspective (pre-show green rooms)

### Venues
- **First Avenue**: Legendary venue, purple neon
- **Let It Be Records**: Real Minneapolis record store (existed 1982-2010s)
- **College Radio**: KJRR represents community broadcasting culture
- **Backstage/Green Room**: Authentic touring band experience

### Items
- **Demo Tape**: Cassettes were primary distribution method
- **Vinyl Record**: Still dominant format in 1982
- **Guitar Pick**: Live performance culture
- **Setlist**: Hand-written, essential touring artifact

---

## Testing & Validation

### Successful Tests
✓ Game runs without errors in headless mode
✓ All 120 validation frames processed successfully
✓ Audio system gracefully handles missing hardware
✓ Zombie music states properly initialized
✓ Diegetic sources load for all rooms
✓ Music tension updates with room context

### Manual Testing Recommendations
1. Test each musical item on different zombie types
2. Verify music effects expire after duration
3. Check multiple sources overlap correctly
4. Confirm room music changes on transitions
5. Validate tension adapts to pacified zombies

---

## Future Enhancements

### Potential Extensions
1. **Combo System**: Using multiple items in sequence for bonus effects
2. **Zombie Memory**: Zombies remember music and become resistant/attracted
3. **Player Music Skills**: Level up musical abilities over time
4. **Band Management**: Recruit zombie musicians for your band
5. **Live Performances**: Play concerts to pacify large groups
6. **Music Collectibles**: Rare vinyls with unique zombie effects

### Audio Improvements
1. **Procedural Melodies**: Generate unique tunes per playthrough
2. **Dynamic Mixing**: More sophisticated audio crossfading
3. **Zombie Vocals**: Music state affects groan harmonics
4. **Environmental Reverb**: Room acoustics affect music propagation

---

## Implementation Summary

**Total Files Modified**: 3
**Total Files Created**: 1
**Lines of Code Added**: ~800
**New Classes**: 2 (ZombieMusicState, DiegeticSource, DiegeticAudioManager)
**New Methods**: 12

### Key Achievements
✓ Music is now a core gameplay mechanic, not just atmosphere
✓ Each zombie type has unique, meaningful music preferences
✓ Players can strategically use musical items to survive
✓ Room-specific audio creates distinct sense of place
✓ Dynamic music responds to both location and threat
✓ Period-authentic 1982 Minneapolis punk/new wave aesthetic maintained

**Music is now MEANINGFUL to gameplay, making Zombie Quest a unique rhythm-survival-adventure hybrid!**
