# Zombie Quest - Signature Audio Themes

## Overview

A legendary audio system featuring period-authentic 1982 synthesis, procedurally generated signature themes, and immersive soundscapes that respond dynamically to gameplay.

---

## 🎵 SIGNATURE THEMES

### 1. **"Neon Dead"** - Main Title Theme
**Style:** Synth-heavy 1982 new wave with ominous undertones

**Musical Features:**
- 8-bar melodic hook (A-C-D-E-F-E-D-C progression)
- A minor pentatonic base (220 Hz / A3)
- 5 layered synthesis channels:
  - Lead sawtooth (warmth)
  - Detuned chorus (analog richness)
  - Sub-bass foundation (ominous undertone)
  - High shimmer (ethereal quality)
  - Modulated pad (slow LFO for movement)

**Usage:**
```python
audio_manager.play_theme(MusicTheme.NEON_DEAD, volume=0.8, loops=-1)
```

**When to Use:** Title screen, main menu

---

### 2. **"Half Alive"** - Maya's Theme
**Style:** Melancholic bass line that evolves from human to zombie

**Musical Features:**
- E minor bass progression (E-G-A-C-B walking bass)
- E2 register (82 Hz) - authentic bassist frequency
- Dynamic transformation system:
  - `dissonance_level=0.0`: Pure human bass (warm, gentle)
  - `dissonance_level=0.3`: Early infection (slight detune)
  - `dissonance_level=0.7`: Losing humanity (harsh harmonics)
  - `dissonance_level=1.0`: Full zombie (distorted, noisy)
- Emotional crescendo capability with natural swells

**Usage:**
```python
# Calculate Maya's transformation stage (0.0 to 1.0)
transformation_stage = maya.zombie_infection_level
audio_manager.play_maya_theme(transformation_stage=transformation_stage, volume=0.7)
```

**When to Use:** Maya confrontation scenes, flashback moments, tragic revelations

---

### 3. **"The Hunger"** - Danger/Proximity Theme
**Style:** Pulsing anxious rhythm with heartbeat bass

**Musical Features:**
- Dynamic BPM system:
  - Base: 80 BPM (distant danger)
  - Max: 140 BPM (immediate threat)
- 6 reactive layers:
  - Heartbeat kick (pulsing low thump)
  - Anxious pulse (mid-range rhythmic)
  - Tension drone (sustained anxiety)
  - High anxiety (nervous vibrato)
  - Health-based distortion (increases as HP drops)
  - Danger harmonic (tritone - devil's interval)

**Usage:**
```python
# Calculate proximity (0.0 = safe, 1.0 = very close)
nearest_zombie_dist = 50  # pixels
max_detection_range = 200
proximity = 1.0 - min(nearest_zombie_dist / max_detection_range, 1.0)

# Get health ratio
health_ratio = player.health / player.max_health

audio_manager.play_danger_theme(proximity=proximity, health_ratio=health_ratio)
```

**Pre-generated Variations:**
- `theme_hunger_distant`: Low proximity, full health
- `theme_hunger_near`: Medium proximity, partial health
- `theme_hunger_critical`: High proximity or low health
- `theme_hunger_dying`: Immediate danger and critical health

**When to Use:** Zombie proximity events, chase sequences, low health warnings

---

### 4. **"Encore"** - Victory Theme
**Style:** Triumphant rock anthem with crowd cheering

**Musical Features:**
- Power chord progression: I-V-vi-IV (E-B-C#m-A)
- E2 base (82 Hz) with authentic rock tone
- 7 celebration layers:
  - Power chord root (distorted square wave)
  - Power chord fifth (harmonic support)
  - Octave doubling (rock thickness)
  - Soaring lead guitar (vibrato, activates in second half)
  - Bass foundation (low-end punch)
  - Crowd cheering (swelling intensity)
  - Cymbal crashes (on chord changes)
- Building energy crescendo over time

**Usage:**
```python
audio_manager.stop_theme(fade_ms=2000)  # Fade out current music
audio_manager.play_theme(MusicTheme.ENCORE, volume=1.0, loops=0)
```

**When to Use:** Good endings, puzzle solutions, saving Maya, victory moments

---

### 5. **"Empty Stage"** - Tragedy Theme
**Style:** Sparse, lonely piano/synth with echoing silence

**Musical Features:**
- E minor sparse melody with long pauses
- Progression: E - [silence] - G - [silence] - A - [silence] - B (sustained)
- E3 register (165 Hz) - intimate piano-like tone
- 7 layers of loneliness:
  - Piano fundamental (pure sine)
  - Piano harmonics (2nd, 3rd, 4th overtones)
  - Subtle pad (underlying loneliness)
  - Echo/reverb (delayed, quieter copy)
  - Room tone (quiet ambient hum)
- Final note fades to nothing (representing loss)

**Usage:**
```python
audio_manager.stop_theme(fade_ms=3000)  # Long fade for emotional impact
audio_manager.play_theme(MusicTheme.EMPTY_STAGE, volume=0.9, loops=0)
```

**When to Use:** Bad endings, character deaths, failed saves, tragic moments

---

## 🧟 ZOMBIE AUDIO PERSONAS

Each zombie type has unique vocal characteristics and musical responses.

### Zombie Types

| Type | Pitch Range | Character | Musical Memory |
|------|------------|-----------|----------------|
| **Scene** | Mid-range (60-90 Hz groan) | Hipster aesthetic | New wave, indie |
| **Bouncer** | Deep (40-70 Hz groan) | Threatening presence | Punk, hardcore |
| **Rocker** | Higher (70-110 Hz groan) | Raspy passion | Rock, metal |
| **DJ** | Modulated (55-85 Hz groan) | Rhythmic qualities | Electronic, dance |

### Special Zombie Sounds

#### 1. **Zombie Remembering**
When zombies hear music they loved in life:
- More melodic vocalizations (major triad progression)
- Reduced aggression (more sine, less noise)
- Gentle vibrato (emotional response)
- Human/zombie ratio shifts with music intensity

```python
if zombie.hears_music_type(music_type) and music_type == zombie.preferred_music:
    audio_manager.play(f'zombie_remembering_{zombie.type}', volume=0.7)
```

#### 2. **Zombie Pacified**
When calmed by music:
- Descending pitch (relaxation)
- Peaceful sine waves (humanity returning)
- Minimal rasp (peaceful state)

```python
if zombie.state == ZombieState.PACIFIED:
    audio_manager.play(f'zombie_pacified_{zombie.type}', volume=0.6)
```

#### 3. **Zombie Death**
Final release sound:
- Type-specific pitch ranges
- Descending pitch (life fading)
- Gurgling texture
- Final breath noise

```python
if zombie.health <= 0:
    audio_manager.play(f'zombie_death_{zombie.type}', volume=0.8)
```

---

## 🎭 ENHANCED ROOM SOUNDSCAPES

All room ambiences feature reactive elements that respond to danger levels.

### Hennepin Outside - Street Atmosphere

**Layers:**
1. Distant traffic rumble (40-55 Hz, slow variation)
2. Wind gusts (variable intensity, natural flow)
3. Occasional sirens (danger atmosphere cue)
4. Neon buzz (1982 street character, 120 Hz + harmonics)
5. Distant club bass (4-on-the-floor pattern from venues)
6. Ambient footsteps (pavement echo)

**Reactive:** Siren frequency increases, wind intensity varies with danger

**Surface Type:** Pavement (concrete footsteps)

---

### Record Store - Vinyl Warmth

**Layers:**
1. Muffled new wave bass (listening booth bleeding through)
2. Vinyl crackle (constant warmth, 22kHz noise)
3. Vinyl rumble (30 Hz low-frequency motor noise)
4. Crowd murmur (browsing conversations, swelling)
5. Cash register dings (occasional, 1200 Hz)
6. Record flipping (every 5 seconds)
7. Wooden floor creaks (180 Hz sawtooth)

**Reactive:** Music volume decreases when danger near

**Surface Type:** Wood floor (creaky footsteps)

---

### College Radio (KJRR) - Broadcast Atmosphere

**Layers:**
1. 60Hz electrical hum (AC power + harmonics at 120Hz, 180Hz)
2. Equipment buzz (850 Hz variable square wave)
3. Tape hiss (32kHz analog character)
4. Turntable motor (33⅓ RPM hum)
5. Microphone feedback (occasional 1200 Hz squeal)
6. DJ headphone bleed (muffled music, 200 Hz square)
7. ON AIR light buzz (120 Hz)
8. Radio static bursts (periodic)

**Reactive:** Interference increases with tension

**Surface Type:** Carpet/linoleum (muffled footsteps)

---

### Backstage - Pre-Show Energy

**Layers:**
1. Amplifier buzz (60Hz + 120Hz ground loop)
2. Muffled drums (4/4 rock pattern: kick on 1&3, snare on 2&4)
3. Bass guitar (E2 to A2, alternating, 82-123 Hz)
4. Guitar tuning (occasional E4 around 330 Hz)
5. Cable interference (crackles and pops)
6. Cymbal wash (distant, high-frequency noise bursts)
7. Equipment movement (cases, amps being moved)
8. Concrete floor footsteps (stage crew)

**Reactive:** Equipment buzz intensifies, tuning becomes more frantic

**Surface Type:** Concrete (hard, echoing footsteps)

---

### Green Room - Intimate Pre-Show

**Layers:**
1. HVAC ventilation (42 Hz drone + air noise)
2. Acoustic guitar tuning/warming up (E3 to B3, occasional)
3. Muffled conversation (band bonding, conversational flow)
4. Footsteps above (venue staff, reverberant)
5. Cassette/boombox (new wave tape with wow/flutter)
6. Tape hiss (28kHz analog warmth)
7. Lighter clicks (nervous smoking, periodic)
8. Nervous tapping/pacing (pre-show jitters)
9. Distant stage rumble (55 Hz)

**Reactive:** Conversation quiets when danger approaches

**Surface Type:** Carpet (muffled, soft footsteps)

---

## 🎮 INTEGRATION GUIDE

### Basic Setup

```python
from zombie_quest.audio import get_audio_manager, MusicTheme, TensionLevel

# Get the global audio manager
audio = get_audio_manager()
```

### Title Screen

```python
def show_title_screen():
    audio.play_theme(MusicTheme.NEON_DEAD, volume=0.8, loops=-1)
```

### Room Transitions

```python
def enter_room(room_id):
    # Set room ambience
    audio.set_room_ambience(room_id)

    # Set music tension
    audio.set_music_tension(TensionLevel.EXPLORATION, room_id)
```

### Dynamic Danger System

```python
def update_danger_audio(player, zombies):
    # Calculate nearest zombie
    nearest_zombie = None
    min_distance = float('inf')

    for zombie in zombies:
        dist = calculate_distance(player.pos, zombie.pos)
        if dist < min_distance:
            min_distance = dist
            nearest_zombie = zombie

    if nearest_zombie and min_distance < 200:
        # Calculate proximity (0.0 to 1.0)
        proximity = 1.0 - (min_distance / 200.0)

        # Calculate health ratio
        health_ratio = player.health / player.max_health

        # Play dynamic danger theme
        audio.play_danger_theme(proximity=proximity, health_ratio=health_ratio)

        # Update ambient intensity
        danger_level = proximity * 0.7 + (1.0 - health_ratio) * 0.3
        audio.update_ambience_intensity(danger_level)
    else:
        # Safe - stop danger theme
        audio.stop_theme(fade_ms=1000)
        audio.update_ambience_intensity(0.0)
```

### Maya Encounter System

```python
def update_maya_scene(maya):
    # Maya's transformation (0.0 = human, 1.0 = full zombie)
    transformation = maya.infection_progress

    audio.play_maya_theme(transformation_stage=transformation, volume=0.8)

    # Special moments
    if transformation >= 0.9 and not maya.crescendo_played:
        # Emotional crescendo moment
        maya.crescendo_played = True
        # Theme automatically has crescendo built in
```

### Zombie Musical Responses

```python
def zombie_hears_music(zombie, diegetic_audio_manager):
    # Get strongest music at zombie position
    music_effect = diegetic_audio_manager.get_strongest_music_at(zombie.pos)

    if music_effect:
        music_type, intensity = music_effect

        # Check if it's the zombie's preferred music
        if music_type == zombie.preferred_music_type:
            # Zombie remembers their humanity
            audio.play(f'zombie_remembering_{zombie.type}', volume=intensity * 0.7)
            zombie.state = ZombieState.REMEMBERING

        elif intensity > 0.5:
            # Music is strong enough to pacify
            audio.play(f'zombie_pacified_{zombie.type}', volume=0.6)
            zombie.state = ZombieState.PACIFIED
```

### Ending Themes

```python
def play_ending(ending_type):
    # Fade out all current audio
    audio.stop_theme(fade_ms=2000)

    if ending_type == "good":
        # Victory - saved the band
        time.sleep(2.5)  # Dramatic pause
        audio.play_theme(MusicTheme.ENCORE, volume=1.0, loops=0)

    elif ending_type == "tragedy":
        # Bad ending - lost Maya
        time.sleep(3.0)  # Longer pause for weight
        audio.play_theme(MusicTheme.EMPTY_STAGE, volume=0.9, loops=0)
```

---

## 🎛️ AUDIO ARCHITECTURE

### Synthesis System

All audio is procedurally generated using:
- **Sample Rate:** 22,050 Hz (period-authentic)
- **Waveforms:** Sine, Square, Triangle, Sawtooth, Noise
- **ADSR Envelopes:** Attack, Decay, Sustain, Release
- **Layered Mixing:** Multiple waveforms per sound

### Channel Allocation

- **Channels 0-3:** Music/Theme channels
- **Channels 4-15:** Sound effects
- **Channels 16-19:** Ambient loops

### Period Authenticity (1982)

- **Synthesis:** Analog-style waveforms (no samples)
- **Effects:** Chorus (detuning), vibrato, tremolo
- **Musical Theory:** Power chords, new wave progressions
- **Frequencies:** Period-accurate AC hum (60Hz), turntable RPM (33⅓)
- **Cultural References:** KJRR radio, Let It Be Records, cassette tapes

---

## 🎼 MUSICAL THEORY NOTES

### Key Signatures
- **Neon Dead:** A minor pentatonic
- **Half Alive:** E minor
- **The Hunger:** Atonal/chromatic (tension)
- **Encore:** E major
- **Empty Stage:** E minor

### Special Intervals
- **Tritone (The Hunger):** 1.414 ratio - "devil's interval" for maximum dissonance
- **Power Chords (Encore):** Root + Perfect Fifth (1.5 ratio) - authentic rock sound
- **Major Triad (Remembering):** Root + Major Third + Perfect Fifth - humanity/memory

### 1982 New Wave Elements
- Sawtooth synth leads (analog warmth)
- Detuned chorus effects
- Arpeggiated basslines
- Square wave pads
- Minimal percussion (electronic)

---

## 📊 Performance Notes

- All sounds are pre-generated on initialization
- Looping sounds use seamless buffers
- Dynamic themes have multiple pre-rendered variations
- Spatial audio uses constant-power panning
- Reactive systems update via volume/pitch modulation (no re-synthesis)

---

## 🎵 Sound List

### Signature Themes
- `theme_neon_dead`
- `theme_maya_human`, `theme_maya_turning`, `theme_maya_lost`, `theme_maya_zombie`
- `theme_hunger_distant`, `theme_hunger_near`, `theme_hunger_critical`, `theme_hunger_dying`
- `theme_encore`
- `theme_empty_stage`

### Zombie Personas (per type: scene, bouncer, rocker, dj)
- `zombie_groan_{type}`
- `zombie_alert_{type}`
- `zombie_attack_{type}`
- `zombie_remembering_{type}` ⭐ NEW
- `zombie_pacified_{type}` ⭐ NEW
- `zombie_death_{type}` ⭐ NEW

### Room Ambiences
- `hennepin_outside`
- `record_store`
- `college_station`
- `backstage_stage`
- `green_room`

---

**Created with legendary audio design expertise for Zombie Quest**
**Period-authentic 1982 synthesis • Emotional narrative arcs • Reactive soundscapes**
