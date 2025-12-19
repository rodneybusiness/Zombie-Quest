# Atmospheric Audio System - 1982 Minneapolis Soundscape

## Overview

The Zombie Quest audio system has been completely rewritten to provide a genuinely atmospheric experience that captures the gritty, neon-soaked vibe of 1982 Minneapolis. The system features advanced synthesis techniques, procedural music, spatial audio, and room-specific soundscapes.

## Features

### 1. Enhanced Sound Synthesis

All sounds are procedurally generated using advanced techniques:

- **Layered Waveforms**: Combines sine, square, triangle, and sawtooth waves
- **ADSR Envelopes**: Proper attack, decay, sustain, and release for natural sound shaping
- **Noise Generation**: Hash-based white noise for realistic textures
- **Bandpass Filtering**: Simple filtering for character and warmth

### 2. Comprehensive Sound Library (30+ Sounds)

#### Movement Sounds
- `footstep` - Default footstep on pavement (layered noise and thump)
- `footstep_concrete` - Sharper attack for hard surfaces
- `footstep_carpet` - Muffled steps on soft surfaces

#### Item Sounds
- `pickup` - Sparkly rising arpeggio when collecting items
- `item_use` - Two-tone confirmation for successful use
- `item_error` - Descending dissonant tone for wrong item

#### Door/Transition Sounds
- `door` - Standard door with descending rumble
- `door_creak` - Creaky old door with warbling
- `door_slam` - Sharp impact sound

#### Combat Sounds
- `hit` - Player damage with falling pitch impact
- `death` - Dramatic descending arpeggio (1.2 seconds)
- `health_low` - Pulsing warning beep

#### Zombie Sounds (Per Type: scene, bouncer, rocker, dj)
- `zombie_groan_{type}` - Type-specific groan with pitch variation
  - Scene: Mid-range hipster groan (60-90Hz)
  - Bouncer: Deep threatening groan (40-70Hz)
  - Rocker: Higher raspy groan (70-110Hz)
  - DJ: Modulated groan (55-85Hz)
- `zombie_alert_{type}` - Rising aggressive vocalization
- `zombie_attack_{type}` - Bite/snap sound
- `zombie_groan` - Generic fallback

#### UI Sounds
- `ui_click` - Short crisp click (1200Hz)
- `ui_select` - Two-tone confirmation beep
- `ui_back` - Descending cancel tone
- `ui_error` - Buzzer sound for invalid actions
- `message` - Rising notification tone
- `success` - Triumphant major arpeggio (C-E-G-C)
- `error` - Descending dissonant failure tone

#### Environmental Sounds
- `electric_hum` - 60Hz electrical hum with harmonics
- `neon_flicker` - High-frequency buzz with irregular modulation
- `vinyl_crackle` - Record surface noise
- `tape_hiss` - Cassette tape hiss

### 3. Procedural Music System

Five layered music tracks that crossfade based on game tension:

#### Music Layers
- **Bass** (55Hz, A1): Foundation layer with simple root-fifth pattern
- **Arpeggio** (220Hz, A3): Minor arpeggio for exploration mood
- **Pad** (440Hz, A4): Sustained chords for atmosphere
- **Pulse** (110Hz, A2): Rhythmic pulse for danger/tension
- **Lead** (880Hz, A5): Minor scale ascent for chase sequences

#### Tension Levels
Music automatically adapts to gameplay:

```python
TensionLevel.MENU       # Bass + Pad (calm)
TensionLevel.SAFE       # Minimal layers, gentle
TensionLevel.EXPLORATION # Normal exploration (bass + arpeggio + pad + light pulse)
TensionLevel.DANGER     # Zombie detected (pulse increases, lead enters)
TensionLevel.CHASE      # Active chase (full intensity, lead prominent)
```

The engine automatically adjusts tension based on:
- Zombie proximity (< 50px = chase, < 100px = danger, < 150px = exploration)
- Number of chasing zombies
- Room zombie count

### 4. Spatial Audio

Sounds are positioned in stereo space with distance attenuation:

```python
# Zombie groans use spatial audio automatically
audio.play_spatial(
    'zombie_groan_rocker',
    source_pos=(zombie_x, zombie_y),
    listener_pos=(hero_x, hero_y),
    volume=0.5,
    fallback_sound='zombie_groan'
)
```

**Features:**
- Constant-power stereo panning based on X position
- Distance attenuation using inverse square law
- Automatic fallback to generic sounds if specific type unavailable

### 5. Room-Specific Ambient Soundscapes

Each room has a unique 3-4 second looping ambient soundscape:

#### Hennepin Avenue Outside (`hennepin_outside`)
- Distant traffic rumble (40-60Hz sine waves)
- Wind noise with modulation
- Occasional distant sirens (600-800Hz warbling)

#### Let It Be Records (`record_store`)
- Muffled bass throb (simulated music from another room)
- Crowd murmur (low-frequency noise)
- Vinyl surface crackle

#### KJRR College Radio (`college_station`)
- 60Hz electrical hum with harmonics
- Equipment buzz (800-900Hz modulated square wave)
- Tape hiss

#### First Avenue Backstage (`backstage_stage`)
- Equipment buzz (120Hz)
- Distant muffled kick drum pattern
- Cable interference noise

#### Green Room (`green_room`)
- HVAC ventilation (40-45Hz warble)
- Distant muffled conversation
- Occasional footsteps from above

Ambience automatically switches when changing rooms with a 500ms crossfade.

### 6. Event-Driven Audio Architecture

The `AudioEventSystem` decouples game events from audio:

```python
# Trigger events from anywhere in the game
audio.event_system.trigger('player_footstep', {})
audio.event_system.trigger('zombie_groan', {
    'x': zombie_x,
    'y': zombie_y,
    'player_x': hero_x,
    'player_y': hero_y,
    'type': 'bouncer'
})
audio.event_system.trigger('room_enter', {'room_id': 'record_store'})
audio.event_system.trigger('music_tension', {'tension': TensionLevel.CHASE})
```

**Built-in Events:**
- `player_footstep` - Play footstep sound
- `player_damage` - Player hit sound
- `player_death` - Death sound
- `item_pickup` - Item collection
- `door_open` - Door transition
- `zombie_groan` - Spatial zombie vocalization
- `zombie_alert` - Zombie aggro sound
- `ui_click`, `ui_select` - UI feedback
- `room_enter` - Trigger room ambience change
- `music_tension` - Set music tension level

## Usage Examples

### Basic Sound Playback

```python
from zombie_quest.audio import get_audio_manager

audio = get_audio_manager()

# Play a sound effect
audio.play('pickup', volume=0.7)
audio.play('zombie_groan_bouncer', volume=0.5)
audio.play('success')
```

### Spatial Audio

```python
# Play sound with position
audio.play_spatial(
    'zombie_groan_dj',
    source_pos=(200, 150),
    listener_pos=(160, 100),
    volume=0.6,
    fallback_sound='zombie_groan'
)
```

### Music Tension Control

```python
from zombie_quest.audio import TensionLevel

# Set music tension
audio.set_music_tension(TensionLevel.CHASE)
audio.set_music_tension(TensionLevel.SAFE)
audio.set_music_tension(TensionLevel.EXPLORATION)
```

### Room Ambience

```python
# Change room ambience
audio.set_room_ambience('record_store')
audio.set_room_ambience('college_station')
```

### Volume Control

```python
# Adjust volumes
audio.set_master_volume(0.8)      # Master (0.0 - 1.0)
audio.set_music_volume(0.6)       # Music layers
audio.set_sfx_volume(0.8)         # Sound effects
audio.set_ambient_volume(0.4)     # Room ambience
```

### Event System

```python
# Use event system for decoupled audio
audio.event_system.trigger('item_pickup', {})

audio.event_system.trigger('zombie_groan', {
    'x': 200,
    'y': 150,
    'player_x': 160,
    'player_y': 100,
    'type': 'rocker'
})

# Register custom event handler
def custom_sound_handler(data):
    audio.play('neon_flicker', volume=0.3)

audio.event_system.register_handler('neon_buzz', custom_sound_handler)
audio.event_system.trigger('neon_buzz', {})
```

### Update Loop Integration

```python
# In your game loop
def update(dt):
    # Update procedural music (crossfading)
    audio.update_music(dt)

    # Your game logic...
```

## Integration in Game Engine

The audio system is fully integrated into the engine:

1. **Initialization**: Audio manager created in `GameEngine.__init__`
2. **Room Changes**: Ambience automatically switches via `change_room()`
3. **Zombie Groans**: Spatial audio in `_update_room()`
4. **Music Tension**: Auto-adjusts in `_update_music_tension()` based on zombie proximity
5. **Combat**: Damage sounds, death sound, low health warning
6. **UI**: Click, select, and feedback sounds throughout interface

## Technical Details

### Audio Settings
- **Sample Rate**: 22050 Hz (retro 8-bit style)
- **Bit Depth**: 16-bit signed
- **Channels**: Stereo (2)
- **Buffer**: 512 samples
- **Mixer Channels**: 20 total (4 music + 12 SFX + 4 ambient)

### Waveform Generation

All sounds use custom waveform generators:

```python
class WaveformGenerator:
    @staticmethod
    def sine(freq, t, phase=0.0) -> float
    def square(freq, t, phase=0.0, duty=0.5) -> float
    def triangle(freq, t, phase=0.0) -> float
    def sawtooth(freq, t, phase=0.0) -> float
    def noise(seed=0) -> float
    def bandpass_filter(signal, freq, center, bandwidth) -> float
```

### ADSR Envelope

```python
@dataclass
class ADSR:
    attack: float = 0.01    # Time to reach peak
    decay: float = 0.1      # Time to sustain level
    sustain: float = 0.7    # Sustain amplitude (0-1)
    release: float = 0.2    # Time to fade out
```

### Spatial Audio Math

**Stereo Panning (Constant Power)**:
```python
relative_pos = (source_x - listener_x) / (room_width / 2)
pan_angle = (relative_pos + 1.0) * π / 4
left_volume = cos(pan_angle)
right_volume = sin(pan_angle)
```

**Distance Attenuation**:
```python
attenuation = 1.0 - (distance / max_distance) ^ 1.5
volume = base_volume * attenuation
```

## Performance

- Sound generation happens at initialization (not runtime)
- ~30 sounds generated in <1 second
- Music updates use simple arithmetic (no audio buffer manipulation)
- Spatial audio calculations are lightweight (2-3 math ops per call)
- Ambient loops use dedicated channels (no CPU for regeneration)

## Customization

### Adding New Sounds

1. Add synthesis function to `AudioManager`:
```python
def _synth_my_sound(self) -> Optional[pygame.mixer.Sound]:
    envelope = ADSR(attack=0.01, decay=0.1, sustain=0.6, release=0.2)

    def gen(t, dur):
        freq = 440
        wave = WaveformGenerator.sine(freq, t)
        return wave * envelope.get_amplitude(t, dur)

    return self._create_sound_buffer(0.5, gen)
```

2. Register in `_generate_all_sounds()`:
```python
self.sounds['my_sound'] = self._synth_my_sound()
```

### Adding New Music Layers

```python
self.music_layers.append(ProceduralMusicLayer(
    name="melody",
    base_freq=440,
    pattern=[0, 2, 4, 5, 7, 5, 4, 2],  # Major scale
    waveform="triangle",
    duration=8.0
))
```

### Adding New Ambience

```python
def _synth_my_room_ambience(self):
    def gen(t, dur):
        # Create unique soundscape
        hum = WaveformGenerator.sine(50, t) * 0.2
        texture = WaveformGenerator.noise(int(t * 1000)) * 0.1
        return hum + texture

    return self._create_sound_buffer(3.0, gen)

# Register it
self.ambience_sounds['my_room'] = self._synth_my_room_ambience()
```

## Troubleshooting

### Audio Not Playing
- Check `audio.initialized` - should be `True`
- Verify pygame mixer initialized without errors
- Check master volume is > 0
- Ensure sound name exists in `audio.sounds`

### Headless/CI Mode
Audio gracefully fails in headless environments:
```python
if not AUDIO_AVAILABLE:
    # All audio calls become no-ops
    return
```

### Performance Issues
- Reduce number of music layers
- Lower ambient volume
- Decrease zombie groan frequency
- Simplify waveform generation (fewer layers)

## 1982 Minneapolis Authenticity

The audio system captures the era through:

1. **Lo-Fi Synthesis**: 22kHz sample rate, simple waveforms = authentic 8-bit texture
2. **Analog Hums**: 60Hz electrical hum (North American AC) in radio station
3. **Tape Artifacts**: Hiss and crackle for period authenticity
4. **Punk/New Wave Sound**: Square waves, distorted tones, minor scales
5. **Neon Buzz**: High-frequency modulated square waves for neon lights
6. **Club Atmosphere**: Muffled bass, distant drums, crowd murmur

The soundscape evokes:
- First Avenue's industrial atmosphere
- College radio's lo-fi equipment
- Record store warmth and vinyl crackle
- Minneapolis winter wind
- Urban street ambience
- 1982 synth-punk aesthetic

## Future Enhancements (Optional)

Possible additions:
- Real-time music generation (streaming instead of pre-rendered loops)
- More complex reverb simulation
- Echo/delay effects for large rooms
- Doppler effect for moving zombies
- Dynamic EQ based on room characteristics
- Footstep variation based on walking speed
- Procedural speech synthesis for zombies
- 1982-authentic drum machine patterns

---

**Enjoy the atmospheric soundscape of 1982 Minneapolis!**
