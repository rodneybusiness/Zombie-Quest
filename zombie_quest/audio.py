"""Atmospheric audio system - 1982 Minneapolis soundscape with signature themes.

Advanced features:
- Layered waveform synthesis with ADSR envelopes
- Procedural music with tension-based layering
- Spatial audio with stereo panning and distance attenuation
- Dynamic zombie vocalizations with pitch variation
- Room-specific ambient soundscapes
- Event-driven audio architecture
- Signature musical themes for key game moments

SIGNATURE THEMES:
================

1. NEON DEAD - Main Title Theme
   Synth-heavy 1982 new wave with ominous undertones.
   8-bar melodic hook that's procedurally generated but consistent.
   Usage:
       audio_manager.play_theme(MusicTheme.NEON_DEAD, volume=0.8, loops=-1)

2. HALF ALIVE - Maya's Theme
   Melancholic bass line that evolves with her transformation.
   Dynamic dissonance based on humanity loss (0.0=human, 1.0=zombie).
   Usage:
       audio_manager.play_maya_theme(transformation_stage=0.5, volume=0.7)

3. THE HUNGER - Danger Theme
   Pulsing anxious rhythm with heartbeat bass.
   Tempo increases with proximity, distortion with health loss.
   Usage:
       audio_manager.play_danger_theme(proximity=0.7, health_ratio=0.4)

4. ENCORE - Victory Theme
   Triumphant rock anthem with power chords and crowd cheering.
   Guitar solo moment and emotional crescendo.
   Usage:
       audio_manager.play_theme(MusicTheme.ENCORE, volume=1.0, loops=0)

5. EMPTY STAGE - Tragedy Theme
   Sparse, lonely piano/synth with echoing silence.
   Represents loss and emptiness in bad endings.
   Usage:
       audio_manager.play_theme(MusicTheme.EMPTY_STAGE, volume=0.9, loops=0)

ZOMBIE AUDIO PERSONAS:
=====================

Each zombie type has unique audio characteristics:
- scene: Mid-range hipster aesthetic
- bouncer: Deep, threatening presence
- rocker: Higher, raspy passion
- dj: Modulated, rhythmic qualities

Special zombie sounds:
- zombie_remembering_{type}: Musical response when hearing loved music
- zombie_pacified_{type}: Peaceful vocalization when calmed
- zombie_death_{type}: Final release sound

ROOM SOUNDSCAPES:
================

Enhanced ambient soundscapes with reactive elements:

Hennepin Outside:
- Traffic rumble, wind, sirens, neon buzz, distant club bass
- Reactive: Siren frequency increases with danger

Record Store:
- New wave bass, vinyl crackle, crowd murmur, cash register, wood floor
- Reactive: Music volume decreases when danger near

College Radio (KJRR):
- 60Hz hum, equipment buzz, tape hiss, turntable motor, feedback
- Reactive: Interference increases with tension

Backstage:
- Amp buzz, muffled drums, guitar tuning, cable interference
- Reactive: Equipment buzz intensifies with proximity

Green Room:
- HVAC, acoustic guitar, conversation, cassette player, nervous energy
- Reactive: Conversation quiets when danger approaches

USAGE EXAMPLES:
==============

# Play title screen music
audio_manager.play_theme(MusicTheme.NEON_DEAD, volume=0.8, loops=-1)

# Play Maya's theme as she transforms
maya_humanity = 1.0 - zombie_progress  # 1.0 to 0.0
audio_manager.play_maya_theme(transformation_stage=zombie_progress)

# Dynamic danger music based on zombie proximity and player health
nearest_zombie_dist = 50  # pixels
max_detection_range = 200
proximity = 1.0 - min(nearest_zombie_dist / max_detection_range, 1.0)
health_ratio = player.health / player.max_health
audio_manager.play_danger_theme(proximity=proximity, health_ratio=health_ratio)

# Play victory theme on good ending
audio_manager.stop_theme(fade_ms=2000)  # Fade out current
audio_manager.play_theme(MusicTheme.ENCORE, volume=1.0, loops=0)

# Reactive room ambience
danger_level = calculate_danger_level()  # 0.0 to 1.0
audio_manager.update_ambience_intensity(danger_level)

# Zombie remembering music
if zombie.hears_favorite_music():
    audio_manager.play(f'zombie_remembering_{zombie.type}', volume=0.7)
"""
from __future__ import annotations

import array
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

# Pygame mixer import with fallback for headless mode
try:
    import pygame.mixer
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

from .config import AUDIO

# Audio constants
SAMPLE_RATE = 22050
MUSIC_CHANNELS = 4  # Background layers for procedural music
SFX_CHANNELS = 12   # Sound effects
AMBIENT_CHANNELS = 4  # Ambient loops


class TensionLevel(Enum):
    """Music tension states."""
    SAFE = 0
    EXPLORATION = 1
    DANGER = 2
    CHASE = 3
    MENU = 4
    TITLE = 5  # Title screen


class MusicTheme(Enum):
    """Named music themes for specific game moments."""
    NEON_DEAD = "neon_dead"           # Main title theme
    HALF_ALIVE = "half_alive"         # Maya's theme
    THE_HUNGER = "the_hunger"         # Danger proximity theme
    ENCORE = "encore"                 # Victory theme
    EMPTY_STAGE = "empty_stage"       # Tragedy theme


@dataclass
class ADSR:
    """ADSR envelope for sound shaping."""
    attack: float = 0.01   # Time to reach peak
    decay: float = 0.1     # Time to sustain level
    sustain: float = 0.7   # Sustain level (0-1)
    release: float = 0.2   # Time to fade out

    def get_amplitude(self, t: float, duration: float) -> float:
        """Get envelope amplitude at time t."""
        if t < 0:
            return 0.0

        # Attack phase
        if t < self.attack:
            return t / self.attack if self.attack > 0 else 1.0

        # Decay phase
        t_decay = t - self.attack
        if t_decay < self.decay:
            peak_to_sustain = 1.0 - self.sustain
            decay_progress = t_decay / self.decay if self.decay > 0 else 1.0
            return 1.0 - (peak_to_sustain * decay_progress)

        # Sustain phase
        sustain_end = duration - self.release
        if t < sustain_end:
            return self.sustain

        # Release phase
        release_progress = (t - sustain_end) / self.release if self.release > 0 else 1.0
        return self.sustain * (1.0 - release_progress)


class WaveformGenerator:
    """Advanced waveform generation with layering and filtering."""

    @staticmethod
    def sine(freq: float, t: float, phase: float = 0.0) -> float:
        """Pure sine wave."""
        return math.sin(2 * math.pi * freq * t + phase)

    @staticmethod
    def square(freq: float, t: float, phase: float = 0.0, duty: float = 0.5) -> float:
        """Square wave with adjustable duty cycle."""
        phase_normalized = (freq * t + phase / (2 * math.pi)) % 1.0
        return 1.0 if phase_normalized < duty else -1.0

    @staticmethod
    def triangle(freq: float, t: float, phase: float = 0.0) -> float:
        """Triangle wave."""
        phase_normalized = (freq * t + phase / (2 * math.pi)) % 1.0
        if phase_normalized < 0.5:
            return 4.0 * phase_normalized - 1.0
        else:
            return 3.0 - 4.0 * phase_normalized

    @staticmethod
    def sawtooth(freq: float, t: float, phase: float = 0.0) -> float:
        """Sawtooth wave."""
        phase_normalized = (freq * t + phase / (2 * math.pi)) % 1.0
        return 2.0 * phase_normalized - 1.0

    @staticmethod
    def noise(seed: int = 0) -> float:
        """White noise using hash-based generation."""
        # Use time-based seed for variation
        hash_val = hash((seed, random.randint(0, 1000000))) % 10000
        return (hash_val / 5000.0) - 1.0

    @staticmethod
    def bandpass_filter(signal: float, freq: float, center: float, bandwidth: float) -> float:
        """Simple bandpass filter approximation."""
        distance = abs(freq - center)
        if distance < bandwidth / 2:
            return signal
        elif distance < bandwidth:
            attenuation = 1.0 - ((distance - bandwidth / 2) / (bandwidth / 2))
            return signal * attenuation
        else:
            return signal * 0.1  # Light bleed through


class SpatialAudio:
    """Handles stereo panning and distance attenuation."""

    @staticmethod
    def calculate_pan(source_x: float, listener_x: float, room_width: float = 320) -> Tuple[float, float]:
        """Calculate stereo pan (left, right) based on position.
        Returns tuple of (left_volume, right_volume) from 0.0 to 1.0.
        """
        # Normalize position (-1 left, 0 center, 1 right)
        relative_pos = (source_x - listener_x) / (room_width / 2)
        relative_pos = max(-1.0, min(1.0, relative_pos))

        # Calculate stereo field (constant power panning)
        pan_angle = (relative_pos + 1.0) * math.pi / 4  # 0 to π/2
        left = math.cos(pan_angle)
        right = math.sin(pan_angle)

        return (left, right)

    @staticmethod
    def calculate_distance_attenuation(distance: float, max_distance: float = 200.0) -> float:
        """Calculate volume attenuation based on distance."""
        if distance <= 0:
            return 1.0
        if distance >= max_distance:
            return 0.0

        # Inverse square law with floor
        attenuation = 1.0 - (distance / max_distance) ** 1.5
        return max(0.0, min(1.0, attenuation))


class ProceduralMusicLayer:
    """Single layer of procedural music."""

    def __init__(self, name: str, base_freq: float, pattern: List[int],
                 waveform: str = "sine", duration: float = 8.0):
        self.name = name
        self.base_freq = base_freq
        self.pattern = pattern  # Musical pattern (semitone offsets)
        self.waveform = waveform
        self.duration = duration
        self.volume = 0.0
        self.target_volume = 0.0
        self.fade_speed = 1.5  # Volume units per second

    def update(self, dt: float):
        """Update layer volume (for crossfading)."""
        if self.volume < self.target_volume:
            self.volume = min(self.target_volume, self.volume + self.fade_speed * dt)
        elif self.volume > self.target_volume:
            self.volume = max(self.target_volume, self.volume - self.fade_speed * dt)

    def generate_sample(self, t: float) -> float:
        """Generate audio sample at time t."""
        # Calculate position in pattern
        beat_duration = self.duration / len(self.pattern)
        pattern_index = int(t / beat_duration) % len(self.pattern)
        semitone_offset = self.pattern[pattern_index]

        # Calculate frequency (A440 standard, 12-tone equal temperament)
        freq = self.base_freq * (2 ** (semitone_offset / 12.0))

        # Generate waveform
        wave_gen = WaveformGenerator()
        if self.waveform == "sine":
            sample = wave_gen.sine(freq, t)
        elif self.waveform == "square":
            sample = wave_gen.square(freq, t, duty=0.3)
        elif self.waveform == "triangle":
            sample = wave_gen.triangle(freq, t)
        elif self.waveform == "sawtooth":
            sample = wave_gen.sawtooth(freq, t)
        else:
            sample = wave_gen.sine(freq, t)

        # Apply volume
        return sample * self.volume


class AudioEventSystem:
    """Event-driven audio system for decoupled game events."""

    def __init__(self, audio_manager: 'AudioManager'):
        self.audio_manager = audio_manager
        self.event_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default event handlers."""
        self.event_handlers = {
            'player_footstep': lambda data: self.audio_manager.play('footstep', volume=0.3),
            'player_damage': lambda data: self.audio_manager.play('hit', volume=0.8),
            'player_death': lambda data: self.audio_manager.play('death', volume=1.0),
            'item_pickup': lambda data: self.audio_manager.play('pickup', volume=0.7),
            'door_open': lambda data: self.audio_manager.play('door', volume=0.6),
            'zombie_groan': self._handle_zombie_groan,
            'zombie_alert': lambda data: self.audio_manager.play('zombie_alert', volume=0.5),
            'ui_click': lambda data: self.audio_manager.play('ui_click', volume=0.5),
            'ui_select': lambda data: self.audio_manager.play('ui_select', volume=0.6),
            'room_enter': self._handle_room_enter,
            'music_tension': self._handle_music_tension,
        }

    def _handle_zombie_groan(self, data: Dict):
        """Handle zombie groan with spatial audio."""
        zombie_x = data.get('x', 160)
        zombie_y = data.get('y', 100)
        player_x = data.get('player_x', 160)
        player_y = data.get('player_y', 100)
        zombie_type = data.get('type', 'scene')

        # Calculate distance
        distance = math.sqrt((zombie_x - player_x)**2 + (zombie_y - player_y)**2)

        # Play with spatial positioning
        self.audio_manager.play_spatial(
            f'zombie_groan_{zombie_type}',
            source_pos=(zombie_x, zombie_y),
            listener_pos=(player_x, player_y),
            fallback_sound='zombie_groan'
        )

    def _handle_room_enter(self, data: Dict):
        """Handle room transition with ambient audio."""
        room_id = data.get('room_id', '')
        self.audio_manager.set_room_ambience(room_id)

    def _handle_music_tension(self, data: Dict):
        """Handle music tension changes."""
        tension = data.get('tension', TensionLevel.EXPLORATION)
        self.audio_manager.set_music_tension(tension)

    def trigger(self, event_name: str, data: Optional[Dict] = None):
        """Trigger an audio event."""
        if event_name in self.event_handlers:
            self.event_handlers[event_name](data or {})

    def register_handler(self, event_name: str, handler: Callable):
        """Register custom event handler."""
        self.event_handlers[event_name] = handler


class AudioManager:
    """Master audio manager with atmospheric synthesis and spatial audio."""

    def __init__(self) -> None:
        self.initialized = False
        self.music_volume = AUDIO.MUSIC_VOLUME
        self.sfx_volume = AUDIO.SFX_VOLUME
        self.ambient_volume = AUDIO.AMBIENT_VOLUME
        self.master_volume = AUDIO.MASTER_VOLUME

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        self.music_paused = False

        # Procedural music system
        self.music_layers: List[ProceduralMusicLayer] = []
        self.current_tension = TensionLevel.EXPLORATION
        self.music_time = 0.0

        # Ambient system
        self.current_room_ambience: Optional[str] = None
        self.ambience_sounds: Dict[str, pygame.mixer.Sound] = {}

        # Event system
        self.event_system: Optional[AudioEventSystem] = None

        # Spatial audio
        self.spatial = SpatialAudio()

        # Initialize
        self._init_audio_system()

    def _init_audio_system(self) -> None:
        """Initialize pygame mixer and generate all sounds."""
        if not AUDIO_AVAILABLE:
            return

        try:
            # Higher quality audio settings
            pygame.mixer.init(
                frequency=SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=512
            )
            pygame.mixer.set_num_channels(MUSIC_CHANNELS + SFX_CHANNELS + AMBIENT_CHANNELS)
            self.initialized = True
        except Exception as e:
            self.initialized = False
            print(f"Audio initialization failed: {e}")
            return

        # Generate all sound effects
        self._generate_all_sounds()

        # Initialize procedural music
        self._init_procedural_music()

        # Initialize event system
        self.event_system = AudioEventSystem(self)

    def _generate_all_sounds(self) -> None:
        """Generate all synthesized sound effects."""
        # Movement sounds
        self.sounds['footstep'] = self._synth_footstep()
        self.sounds['footstep_concrete'] = self._synth_footstep_concrete()
        self.sounds['footstep_carpet'] = self._synth_footstep_carpet()

        # Item sounds
        self.sounds['pickup'] = self._synth_pickup()
        self.sounds['item_use'] = self._synth_item_use()
        self.sounds['item_error'] = self._synth_item_error()

        # Door/transition sounds
        self.sounds['door'] = self._synth_door()
        self.sounds['door_creak'] = self._synth_door_creak()
        self.sounds['door_slam'] = self._synth_door_slam()

        # Combat sounds
        self.sounds['hit'] = self._synth_hit()
        self.sounds['death'] = self._synth_death()
        self.sounds['health_low'] = self._synth_health_low()

        # Zombie sounds (multiple types with variations)
        for zombie_type in ['scene', 'bouncer', 'rocker', 'dj']:
            self.sounds[f'zombie_groan_{zombie_type}'] = self._synth_zombie_groan(zombie_type)
            self.sounds[f'zombie_alert_{zombie_type}'] = self._synth_zombie_alert(zombie_type)
            self.sounds[f'zombie_attack_{zombie_type}'] = self._synth_zombie_attack(zombie_type)

            # Enhanced zombie audio personas
            self.sounds[f'zombie_remembering_{zombie_type}'] = self._synth_zombie_remembering(zombie_type, music_intensity=0.6)
            self.sounds[f'zombie_pacified_{zombie_type}'] = self._synth_zombie_pacified(zombie_type)
            self.sounds[f'zombie_death_{zombie_type}'] = self._synth_zombie_death(zombie_type)

        # Generic zombie sounds (fallbacks)
        self.sounds['zombie_groan'] = self._synth_zombie_groan('scene')
        self.sounds['zombie_alert'] = self._synth_zombie_alert('scene')
        self.sounds['zombie_remembering'] = self._synth_zombie_remembering('scene')
        self.sounds['zombie_pacified'] = self._synth_zombie_pacified('scene')
        self.sounds['zombie_death'] = self._synth_zombie_death('scene')

        # UI sounds
        self.sounds['ui_click'] = self._synth_ui_click()
        self.sounds['ui_select'] = self._synth_ui_select()
        self.sounds['ui_back'] = self._synth_ui_back()
        self.sounds['ui_error'] = self._synth_ui_error()
        self.sounds['message'] = self._synth_message()
        self.sounds['success'] = self._synth_success()
        self.sounds['error'] = self._synth_error()

        # Environmental sounds
        self.sounds['electric_hum'] = self._synth_electric_hum()
        self.sounds['neon_flicker'] = self._synth_neon_flicker()
        self.sounds['vinyl_crackle'] = self._synth_vinyl_crackle()
        self.sounds['tape_hiss'] = self._synth_tape_hiss()

        # Generate ambient soundscapes
        self._generate_ambient_soundscapes()

        # Generate signature music themes
        self._generate_signature_themes()

    def _create_sound_buffer(self, duration: float, generator: Callable,
                            stereo: bool = False) -> Optional[pygame.mixer.Sound]:
        """Create a sound from a generator function.

        Args:
            duration: Sound duration in seconds
            generator: Function(t, duration) -> float or (left, right) tuple
            stereo: If True, generator returns (left, right) tuple
        """
        if not self.initialized:
            return None

        num_samples = int(SAMPLE_RATE * duration)

        if stereo:
            # Stereo sound
            samples = array.array('h', [0] * (num_samples * 2))
            for i in range(num_samples):
                t = i / SAMPLE_RATE
                left, right = generator(t, duration)
                samples[i * 2] = int(left * 32767 * 0.5)
                samples[i * 2 + 1] = int(right * 32767 * 0.5)
        else:
            # Mono sound
            samples = array.array('h', [0] * num_samples)
            for i in range(num_samples):
                t = i / SAMPLE_RATE
                samples[i] = int(generator(t, duration) * 32767 * 0.5)

        try:
            sound = pygame.mixer.Sound(buffer=samples)
            return sound
        except Exception as e:
            print(f"Failed to create sound: {e}")
            return None

    # ==================== MOVEMENT SOUNDS ====================

    def _synth_footstep(self) -> Optional[pygame.mixer.Sound]:
        """Footstep on pavement - layered noise and thump."""
        envelope = ADSR(attack=0.005, decay=0.03, sustain=0.3, release=0.05)

        def gen(t, dur):
            # Low thump
            thump = WaveformGenerator.sine(80, t) * 0.4
            # Mid crunch
            crunch_freq = 150 + 50 * math.sin(t * 80)
            crunch = WaveformGenerator.square(crunch_freq, t, duty=0.3) * 0.3
            # High noise
            noise = WaveformGenerator.noise(int(t * 10000)) * 0.3

            mix = thump + crunch + noise
            return mix * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.12, gen)

    def _synth_footstep_concrete(self) -> Optional[pygame.mixer.Sound]:
        """Footstep on concrete - sharper attack."""
        envelope = ADSR(attack=0.002, decay=0.02, sustain=0.2, release=0.04)

        def gen(t, dur):
            thump = WaveformGenerator.sine(120, t) * 0.5
            click = WaveformGenerator.noise(int(t * 20000)) * 0.5
            return (thump + click) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.1, gen)

    def _synth_footstep_carpet(self) -> Optional[pygame.mixer.Sound]:
        """Muffled footstep on carpet."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.4, release=0.08)

        def gen(t, dur):
            thump = WaveformGenerator.sine(60, t) * 0.6
            rustle = WaveformGenerator.noise(int(t * 5000)) * 0.4
            return (thump + rustle) * envelope.get_amplitude(t, dur) * 0.7

        return self._create_sound_buffer(0.15, gen)

    # ==================== ITEM SOUNDS ====================

    def _synth_pickup(self) -> Optional[pygame.mixer.Sound]:
        """Item pickup - sparkly arpeggio."""
        envelope = ADSR(attack=0.01, decay=0.1, sustain=0.6, release=0.2)

        def gen(t, dur):
            # Rising arpeggio
            progress = t / dur
            base_freq = 800
            freq = base_freq * (1 + progress * 0.8)

            # Layered tones
            fundamental = WaveformGenerator.sine(freq, t) * 0.5
            harmonic = WaveformGenerator.sine(freq * 2, t) * 0.3
            shimmer = WaveformGenerator.triangle(freq * 4, t) * 0.2

            mix = fundamental + harmonic + shimmer
            return mix * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.35, gen)

    def _synth_item_use(self) -> Optional[pygame.mixer.Sound]:
        """Item successfully used."""
        envelope = ADSR(attack=0.02, decay=0.08, sustain=0.5, release=0.15)

        def gen(t, dur):
            # Two-tone confirmation
            freq = 600 if t < dur / 2 else 800
            tone = WaveformGenerator.sine(freq, t) * 0.6
            overtone = WaveformGenerator.sine(freq * 1.5, t) * 0.4
            return (tone + overtone) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.25, gen)

    def _synth_item_error(self) -> Optional[pygame.mixer.Sound]:
        """Wrong item used."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.6, release=0.12)

        def gen(t, dur):
            # Descending dissonant tones
            progress = t / dur
            freq = 400 - 200 * progress
            tone = WaveformGenerator.square(freq, t, duty=0.4) * 0.7
            dissonance = WaveformGenerator.sine(freq * 1.1, t) * 0.3
            return (tone + dissonance) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.3, gen)

    # ==================== DOOR SOUNDS ====================

    def _synth_door(self) -> Optional[pygame.mixer.Sound]:
        """Standard door transition."""
        envelope = ADSR(attack=0.05, decay=0.15, sustain=0.5, release=0.3)

        def gen(t, dur):
            # Low rumble with descending pitch
            progress = t / dur
            freq = 100 - 30 * progress
            rumble = WaveformGenerator.sine(freq, t) * 0.6
            creak = WaveformGenerator.sawtooth(freq * 2.5, t) * 0.4
            return (rumble + creak) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.5, gen)

    def _synth_door_creak(self) -> Optional[pygame.mixer.Sound]:
        """Creaky old door."""
        envelope = ADSR(attack=0.08, decay=0.2, sustain=0.4, release=0.4)

        def gen(t, dur):
            # Warbling creak
            freq = 200 + 50 * math.sin(t * 12)
            creak = WaveformGenerator.sawtooth(freq, t) * 0.7
            squeak = WaveformGenerator.square(freq * 1.5, t, duty=0.2) * 0.3
            return (creak + squeak) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.7, gen)

    def _synth_door_slam(self) -> Optional[pygame.mixer.Sound]:
        """Door slamming shut."""
        envelope = ADSR(attack=0.001, decay=0.05, sustain=0.2, release=0.15)

        def gen(t, dur):
            # Sharp impact
            impact = WaveformGenerator.noise(int(t * 30000)) * 0.6
            thud = WaveformGenerator.sine(60, t) * 0.4
            return (impact + thud) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.25, gen)

    # ==================== COMBAT SOUNDS ====================

    def _synth_hit(self) -> Optional[pygame.mixer.Sound]:
        """Player takes damage."""
        envelope = ADSR(attack=0.005, decay=0.08, sustain=0.3, release=0.15)

        def gen(t, dur):
            # Impact with falling pitch
            progress = t / dur
            freq = 250 - 180 * progress
            impact = WaveformGenerator.square(freq, t, duty=0.3) * 0.5
            noise = WaveformGenerator.noise(int(t * 15000)) * 0.5
            return (impact + noise) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.25, gen)

    def _synth_death(self) -> Optional[pygame.mixer.Sound]:
        """Player death - dramatic descending tone."""
        envelope = ADSR(attack=0.05, decay=0.3, sustain=0.6, release=0.5)

        def gen(t, dur):
            # Dramatic descending arpeggio
            progress = t / dur
            freq = 400 * (1 - progress * 0.85)

            fundamental = WaveformGenerator.sine(freq, t) * 0.5
            fifth = WaveformGenerator.sine(freq * 1.5, t) * 0.3
            noise = WaveformGenerator.noise(int(t * 8000)) * 0.2 * progress

            mix = fundamental + fifth + noise
            return mix * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(1.2, gen)

    def _synth_health_low(self) -> Optional[pygame.mixer.Sound]:
        """Warning beep for low health."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.7, release=0.1)

        def gen(t, dur):
            # Pulsing warning tone
            freq = 800 + 200 * math.sin(t * 25)
            beep = WaveformGenerator.square(freq, t, duty=0.5) * 0.8
            return beep * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.2, gen)

    # ==================== ZOMBIE SOUNDS ====================

    def _synth_zombie_groan(self, zombie_type: str) -> Optional[pygame.mixer.Sound]:
        """Zombie groan with type variation."""
        # Different zombies have different pitch ranges
        pitch_ranges = {
            'scene': (60, 90),      # Mid-range hipster groan
            'bouncer': (40, 70),    # Deep threatening groan
            'rocker': (70, 110),    # Higher raspy groan
            'dj': (55, 85)          # Modulated groan
        }

        low_freq, high_freq = pitch_ranges.get(zombie_type, (60, 90))

        envelope = ADSR(attack=0.1, decay=0.2, sustain=0.7, release=0.3)

        def gen(t, dur):
            # Warbling groan
            base_freq = low_freq + (high_freq - low_freq) * 0.5
            freq = base_freq + 15 * math.sin(t * 4) + 5 * math.sin(t * 7)

            # Layered vocal-like texture
            fundamental = WaveformGenerator.sine(freq, t) * 0.4
            formant1 = WaveformGenerator.sine(freq * 2.5, t) * 0.3
            formant2 = WaveformGenerator.sine(freq * 3.8, t) * 0.2
            rasp = WaveformGenerator.noise(int(t * 1000)) * 0.1

            mix = fundamental + formant1 + formant2 + rasp
            return mix * envelope.get_amplitude(t, dur) * 0.6

        duration = random.uniform(0.6, 1.0)
        return self._create_sound_buffer(duration, gen)

    def _synth_zombie_alert(self, zombie_type: str) -> Optional[pygame.mixer.Sound]:
        """Zombie alert/aggro sound."""
        pitch_ranges = {
            'scene': (80, 120),
            'bouncer': (60, 100),
            'rocker': (90, 140),
            'dj': (70, 110)
        }

        low_freq, high_freq = pitch_ranges.get(zombie_type, (80, 120))

        envelope = ADSR(attack=0.05, decay=0.1, sustain=0.6, release=0.2)

        def gen(t, dur):
            # Rising aggressive groan
            progress = t / dur
            freq = low_freq + (high_freq - low_freq) * progress
            freq += 10 * math.sin(t * 15)

            tone = WaveformGenerator.square(freq, t, duty=0.4) * 0.5
            growl = WaveformGenerator.sawtooth(freq * 0.5, t) * 0.3
            rasp = WaveformGenerator.noise(int(t * 3000)) * 0.2

            mix = tone + growl + rasp
            return mix * envelope.get_amplitude(t, dur) * 0.7

        return self._create_sound_buffer(0.4, gen)

    def _synth_zombie_attack(self, zombie_type: str) -> Optional[pygame.mixer.Sound]:
        """Zombie attack vocalization."""
        envelope = ADSR(attack=0.02, decay=0.08, sustain=0.5, release=0.15)

        def gen(t, dur):
            # Aggressive bite/snap sound
            freq = 150 + 80 * math.sin(t * 20)
            snap = WaveformGenerator.square(freq, t, duty=0.2) * 0.6
            noise = WaveformGenerator.noise(int(t * 10000)) * 0.4
            return (snap + noise) * envelope.get_amplitude(t, dur) * 0.8

        return self._create_sound_buffer(0.3, gen)

    # ==================== UI SOUNDS ====================

    def _synth_ui_click(self) -> Optional[pygame.mixer.Sound]:
        """UI click - short and crisp."""
        envelope = ADSR(attack=0.005, decay=0.02, sustain=0.0, release=0.03)

        def gen(t, dur):
            click = WaveformGenerator.sine(1200, t) * 0.8
            return click * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.06, gen)

    def _synth_ui_select(self) -> Optional[pygame.mixer.Sound]:
        """UI selection confirmation."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.4, release=0.1)

        def gen(t, dur):
            # Two-tone beep
            freq = 800 if t < dur * 0.4 else 1000
            tone = WaveformGenerator.sine(freq, t) * 0.7
            return tone * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.18, gen)

    def _synth_ui_back(self) -> Optional[pygame.mixer.Sound]:
        """UI back/cancel sound."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.4, release=0.1)

        def gen(t, dur):
            # Descending tone
            freq = 900 - 300 * (t / dur)
            tone = WaveformGenerator.sine(freq, t) * 0.6
            return tone * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.15, gen)

    def _synth_ui_error(self) -> Optional[pygame.mixer.Sound]:
        """UI error/invalid action."""
        envelope = ADSR(attack=0.01, decay=0.05, sustain=0.5, release=0.1)

        def gen(t, dur):
            # Buzzer sound
            freq = 220
            buzz = WaveformGenerator.square(freq, t, duty=0.5) * 0.7
            return buzz * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.2, gen)

    def _synth_message(self) -> Optional[pygame.mixer.Sound]:
        """Message notification."""
        envelope = ADSR(attack=0.02, decay=0.06, sustain=0.3, release=0.08)

        def gen(t, dur):
            freq = 500 + 150 * (t / dur)
            tone = WaveformGenerator.sine(freq, t) * 0.5
            return tone * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.12, gen)

    def _synth_success(self) -> Optional[pygame.mixer.Sound]:
        """Success/unlock sound - triumphant arpeggio."""
        envelope = ADSR(attack=0.02, decay=0.1, sustain=0.6, release=0.2)

        def gen(t, dur):
            # Major triad arpeggio (C-E-G-C)
            beat = int(t / (dur / 4))
            freqs = [523, 659, 784, 1047]  # C5, E5, G5, C6
            freq = freqs[min(beat, 3)]

            tone = WaveformGenerator.sine(freq, t) * 0.6
            harmonic = WaveformGenerator.sine(freq * 2, t) * 0.4
            return (tone + harmonic) * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.5, gen)

    def _synth_error(self) -> Optional[pygame.mixer.Sound]:
        """Error/failure sound."""
        envelope = ADSR(attack=0.02, decay=0.08, sustain=0.5, release=0.15)

        def gen(t, dur):
            # Descending dissonant tone
            progress = t / dur
            freq = 300 - 100 * progress
            tone = WaveformGenerator.square(freq, t, duty=0.5) * 0.7
            return tone * envelope.get_amplitude(t, dur)

        return self._create_sound_buffer(0.35, gen)

    # ==================== ENVIRONMENTAL SOUNDS ====================

    def _synth_electric_hum(self) -> Optional[pygame.mixer.Sound]:
        """60Hz electrical hum with harmonics."""
        def gen(t, dur):
            # 60Hz + harmonics (North American AC)
            fundamental = WaveformGenerator.sine(60, t) * 0.3
            harmonic2 = WaveformGenerator.sine(120, t) * 0.2
            harmonic3 = WaveformGenerator.sine(180, t) * 0.1

            # Slight modulation
            mod = 1.0 + 0.05 * math.sin(t * 7)

            return (fundamental + harmonic2 + harmonic3) * mod * 0.4

        return self._create_sound_buffer(2.0, gen)

    def _synth_neon_flicker(self) -> Optional[pygame.mixer.Sound]:
        """Neon light flicker/buzz."""
        def gen(t, dur):
            # High frequency buzz with irregular modulation
            base_freq = 800 + 200 * math.sin(t * 13)
            buzz = WaveformGenerator.square(base_freq, t, duty=0.3) * 0.3

            # Random flicker
            flicker = 1.0 if (int(t * 20) % 7) != 0 else 0.3

            return buzz * flicker * 0.3

        return self._create_sound_buffer(1.5, gen)

    def _synth_vinyl_crackle(self) -> Optional[pygame.mixer.Sound]:
        """Vinyl record surface noise."""
        def gen(t, dur):
            # Filtered noise
            noise = WaveformGenerator.noise(int(t * 44100))
            # Low-pass effect (simple)
            filtered = noise * (0.5 + 0.5 * math.sin(t * 100))
            return filtered * 0.2

        return self._create_sound_buffer(2.0, gen)

    def _synth_tape_hiss(self) -> Optional[pygame.mixer.Sound]:
        """Cassette tape hiss."""
        def gen(t, dur):
            # High frequency filtered noise
            noise = WaveformGenerator.noise(int(t * 44100))
            # Simple high-pass effect
            hiss = noise * (0.7 + 0.3 * math.sin(t * 200))
            return hiss * 0.15

        return self._create_sound_buffer(2.0, gen)

    # ==================== SIGNATURE MUSIC THEMES ====================

    def _synth_neon_dead_theme(self) -> Optional[pygame.mixer.Sound]:
        """MAIN THEME: 'Neon Dead' - Synth-heavy 1982 new wave title screen.

        Ominous undertones with a memorable 8-bar melody hook.
        Procedurally generated but consistent using fixed seed.
        """
        envelope = ADSR(attack=0.05, decay=0.2, sustain=0.8, release=0.4)

        # 8-bar hook melody (semitone offsets from A minor pentatonic)
        melody_pattern = [0, 3, 5, 7, 8, 7, 5, 3]  # A-C-D-E-F-E-D-C
        bar_duration = 0.5  # Each note lasts 0.5 seconds
        total_duration = len(melody_pattern) * bar_duration

        def gen(t, dur):
            # Determine current note in pattern
            pattern_time = t % total_duration
            note_index = int(pattern_time / bar_duration)
            semitone = melody_pattern[note_index]

            # Base frequency A3 (220 Hz) - iconic new wave register
            base_freq = 220
            freq = base_freq * (2 ** (semitone / 12.0))

            # Layer 1: Main synth lead (sawtooth for warmth)
            lead = WaveformGenerator.sawtooth(freq, t) * 0.4

            # Layer 2: Detuned layer for chorus effect
            detuned = WaveformGenerator.sawtooth(freq * 1.02, t + 0.01) * 0.3

            # Layer 3: Sub-bass foundation (ominous undertone)
            bass_freq = freq / 2
            bass = WaveformGenerator.sine(bass_freq, t) * 0.5

            # Layer 4: High shimmer (triangle for ethereal quality)
            shimmer = WaveformGenerator.triangle(freq * 2, t) * 0.2

            # Layer 5: Ominous pad (slow modulated sine)
            pad_freq = freq * 0.5
            pad_mod = 1.0 + 0.1 * math.sin(t * 0.5)  # Slow LFO
            pad = WaveformGenerator.sine(pad_freq, t) * 0.3 * pad_mod

            # Mix all layers
            mix = lead + detuned + bass + shimmer + pad

            # Apply envelope with looping consideration
            note_time = pattern_time % bar_duration
            amplitude = envelope.get_amplitude(note_time, bar_duration)

            return mix * amplitude * 0.35  # Master volume

        return self._create_sound_buffer(total_duration, gen)

    def _synth_half_alive_theme(self, dissonance_level: float = 0.0) -> Optional[pygame.mixer.Sound]:
        """MAYA'S THEME: 'Half Alive' - Melancholic bass line for the bassist.

        Args:
            dissonance_level: 0.0 (human) to 1.0 (full zombie) - adds discord

        Starts with a beautiful human bass line, gradually adds dissonance
        as she loses her humanity. Emotional crescendo capability.
        """
        envelope = ADSR(attack=0.08, decay=0.15, sustain=0.85, release=0.5)

        # Melancholic bass progression (E minor feel)
        # E-G-A-C-B pattern (bassist's walking line)
        bass_pattern = [0, 3, 5, 8, 7]  # From E2 (82 Hz)
        note_duration = 0.8
        total_duration = len(bass_pattern) * note_duration

        def gen(t, dur):
            # Current note
            pattern_time = t % total_duration
            note_index = int(pattern_time / note_duration)
            semitone = bass_pattern[note_index]

            # Bass frequency E2 (82 Hz) - bassist register
            base_freq = 82
            freq = base_freq * (2 ** (semitone / 12.0))

            # Layer 1: Deep bass fundamental (sine for warmth)
            fundamental = WaveformGenerator.sine(freq, t) * 0.6

            # Layer 2: Bass harmonic (gives definition)
            harmonic = WaveformGenerator.sine(freq * 2, t) * 0.3

            # Layer 3: Human element - gentle triangle wave
            human_tone = WaveformGenerator.triangle(freq * 1.5, t) * (0.25 * (1.0 - dissonance_level))

            # Layer 4: Zombie dissonance - increases with transformation
            # Detuned, harsh square wave
            dissonant_freq = freq * (1.0 + 0.05 * dissonance_level)  # Slight detune
            dissonance = WaveformGenerator.square(dissonant_freq, t, duty=0.3) * (0.4 * dissonance_level)

            # Layer 5: Emotional pad - fades as humanity fades
            pad = WaveformGenerator.sine(freq * 0.5, t) * (0.2 * (1.0 - dissonance_level * 0.5))

            # Layer 6: Distortion/noise - increases with zombie transformation
            noise = WaveformGenerator.noise(int(t * 1000)) * (0.15 * dissonance_level)

            # Crescendo capability - volume swell based on time
            crescendo = 1.0 + 0.3 * math.sin(t * 0.3)  # Gentle swell

            # Mix
            mix = fundamental + harmonic + human_tone + dissonance + pad + noise

            # Apply envelope
            note_time = pattern_time % note_duration
            amplitude = envelope.get_amplitude(note_time, note_duration)

            return mix * amplitude * crescendo * 0.4

        return self._create_sound_buffer(total_duration, gen)

    def _synth_the_hunger_theme(self, proximity: float = 0.5, health_ratio: float = 1.0) -> Optional[pygame.mixer.Sound]:
        """DANGER THEME: 'The Hunger' - Pulsing anxious rhythm with heartbeat bass.

        Args:
            proximity: 0.0 (far) to 1.0 (very close) - increases tempo
            health_ratio: 1.0 (full health) to 0.0 (near death) - adds distortion

        Dynamic theme that responds to danger level and player health.
        """
        # Tempo increases with proximity
        base_bpm = 80
        max_bpm = 140
        bpm = base_bpm + (max_bpm - base_bpm) * proximity
        beat_duration = 60.0 / bpm

        envelope = ADSR(attack=0.02, decay=0.08, sustain=0.6, release=0.15)

        def gen(t, dur):
            # Heartbeat pattern (kick-rest-kick-rest)
            beat_phase = (t % beat_duration) / beat_duration
            is_beat = beat_phase < 0.3  # Beat occurs in first 30% of cycle

            # Layer 1: Heartbeat kick (low thump)
            kick_freq = 60 - 20 * beat_phase  # Descending pitch on beat
            kick = WaveformGenerator.sine(kick_freq, t) * (0.8 if is_beat else 0.0)

            # Layer 2: Anxious pulse (mid-range rhythmic element)
            pulse_freq = 220 * (1.0 + 0.2 * proximity)  # Higher with proximity
            pulse_rhythm = math.sin(t * bpm / 15) ** 2  # Pulsing rhythm
            pulse = WaveformGenerator.square(pulse_freq, t, duty=0.25) * pulse_rhythm * 0.3

            # Layer 3: Tension drone (sustained anxiety)
            drone_freq = 110 + 50 * proximity
            drone = WaveformGenerator.sawtooth(drone_freq, t) * 0.25

            # Layer 4: High anxiety (nervous energy)
            anxiety_freq = 880 + 440 * proximity
            anxiety_mod = 1.0 + 0.3 * math.sin(t * 7)  # Nervous vibrato
            anxiety = WaveformGenerator.triangle(anxiety_freq, t) * anxiety_mod * proximity * 0.2

            # Layer 5: Health-based distortion (increases as health drops)
            distortion_amount = 1.0 - health_ratio
            distortion = WaveformGenerator.noise(int(t * 5000)) * distortion_amount * 0.3

            # Layer 6: Danger harmonic (dissonant overtone)
            danger_freq = drone_freq * 1.414  # Tritone (devil's interval)
            danger = WaveformGenerator.sine(danger_freq, t) * proximity * 0.2

            # Mix
            mix = kick + pulse + drone + anxiety + distortion + danger

            # Overall envelope
            amplitude = envelope.get_amplitude(beat_phase * beat_duration, beat_duration)

            # Intensity increases with both proximity and low health
            intensity = 0.5 + 0.3 * proximity + 0.2 * distortion_amount

            return mix * amplitude * intensity * 0.35

        return self._create_sound_buffer(2.0, gen)

    def _synth_encore_theme(self) -> Optional[pygame.mixer.Sound]:
        """VICTORY THEME: 'Encore' - Triumphant rock anthem with crowd cheering.

        Plays on good endings. Features triumphant power chords,
        soaring lead, crowd cheering layer, and a guitar solo moment.
        """
        envelope = ADSR(attack=0.05, decay=0.15, sustain=0.8, release=0.6)

        # Triumphant progression: I-V-vi-IV (E-B-C#m-A)
        # Using power chords (root + fifth)
        chord_pattern = [
            (0, 7),    # E power chord (E-B)
            (7, 14),   # B power chord (B-F#)
            (4, 11),   # C# power chord (C#-G#)
            (5, 12),   # A power chord (A-E)
        ]
        chord_duration = 1.0
        total_duration = len(chord_pattern) * chord_duration

        def gen(t, dur):
            # Current chord
            pattern_time = t % total_duration
            chord_index = int(pattern_time / chord_duration)
            root_semitone, fifth_semitone = chord_pattern[chord_index]

            # Base frequency E2 (82 Hz)
            base_freq = 82
            root_freq = base_freq * (2 ** (root_semitone / 12.0))
            fifth_freq = base_freq * (2 ** (fifth_semitone / 12.0))

            # Layer 1: Power chord root (square wave - distorted guitar tone)
            root = WaveformGenerator.square(root_freq, t, duty=0.4) * 0.4

            # Layer 2: Power chord fifth
            fifth = WaveformGenerator.square(fifth_freq, t, duty=0.4) * 0.35

            # Layer 3: Octave doubling (rock thickness)
            octave = WaveformGenerator.square(root_freq * 2, t, duty=0.3) * 0.25

            # Layer 4: Lead guitar (soaring melody)
            # Guitar solo moment in second half
            lead_active = pattern_time > total_duration / 2
            lead_freq = root_freq * 4 * (1.0 + 0.02 * math.sin(t * 6))  # Vibrato
            lead = WaveformGenerator.sawtooth(lead_freq, t) * (0.5 if lead_active else 0.2)

            # Layer 5: Bass foundation
            bass = WaveformGenerator.sine(root_freq / 2, t) * 0.4

            # Layer 6: Crowd cheering (filtered noise with rhythm)
            crowd_intensity = 0.7 + 0.3 * math.sin(t * 1.5)  # Swelling crowd
            crowd = WaveformGenerator.noise(int(t * 3000)) * crowd_intensity * 0.2

            # Layer 7: Cymbal crash on chord changes
            crash_phase = (pattern_time % chord_duration) / chord_duration
            is_crash = crash_phase < 0.1
            crash = WaveformGenerator.noise(int(t * 20000)) * (0.4 if is_crash else 0.0)

            # Mix
            mix = root + fifth + octave + lead + bass + crowd + crash

            # Apply envelope
            chord_time = pattern_time % chord_duration
            amplitude = envelope.get_amplitude(chord_time, chord_duration)

            # Triumphant energy builds over time
            energy = 0.7 + 0.3 * (pattern_time / total_duration)

            return mix * amplitude * energy * 0.3

        return self._create_sound_buffer(total_duration, gen)

    def _synth_empty_stage_theme(self) -> Optional[pygame.mixer.Sound]:
        """TRAGEDY THEME: 'Empty Stage' - Sparse, lonely piano/synth.

        Plays on bad endings. Features echoing silence, sparse piano-like notes,
        and a single sustained note fade representing loss and emptiness.
        """
        envelope = ADSR(attack=0.15, decay=0.3, sustain=0.6, release=2.0)  # Long release for echo

        # Sparse, melancholic melody (E minor, whole notes)
        # Long pauses between notes create emptiness
        melody_pattern = [
            (0, 2.0),   # E - held
            (-1, 1.5),  # Silence
            (3, 2.0),   # G - held
            (-1, 1.5),  # Silence
            (5, 2.0),   # A - held
            (-1, 1.5),  # Silence
            (7, 3.0),   # B - final sustained note
        ]

        total_duration = sum(duration for _, duration in melody_pattern)

        def gen(t, dur):
            # Find current note
            current_time = 0
            current_semitone = -1  # Silence
            note_start = 0
            note_duration = 0

            for semitone, length in melody_pattern:
                if t >= current_time and t < current_time + length:
                    current_semitone = semitone
                    note_start = current_time
                    note_duration = length
                    break
                current_time += length

            # Silence
            if current_semitone == -1:
                # Very quiet room tone (echoing silence)
                room_tone = WaveformGenerator.sine(40, t) * 0.02
                return room_tone

            # Piano-like tone (E3 = 165 Hz base)
            base_freq = 165
            freq = base_freq * (2 ** (current_semitone / 12.0))

            # Time within this note
            note_time = t - note_start

            # Layer 1: Piano fundamental (sine for pure tone)
            fundamental = WaveformGenerator.sine(freq, t) * 0.5

            # Layer 2: Piano harmonics (for piano-like timbre)
            harmonic2 = WaveformGenerator.sine(freq * 2, t) * 0.2
            harmonic3 = WaveformGenerator.sine(freq * 3, t) * 0.1
            harmonic4 = WaveformGenerator.sine(freq * 4, t) * 0.05

            # Layer 3: Subtle pad (loneliness)
            pad = WaveformGenerator.triangle(freq * 0.5, t) * 0.15

            # Layer 4: Echo/reverb simulation (delayed, quieter copy)
            echo_delay = 0.3
            if note_time > echo_delay:
                echo_time = note_time - echo_delay
                echo = WaveformGenerator.sine(freq, t - echo_delay) * 0.2
            else:
                echo = 0

            # Mix
            mix = fundamental + harmonic2 + harmonic3 + harmonic4 + pad + echo

            # Apply envelope
            amplitude = envelope.get_amplitude(note_time, note_duration)

            # Final note has extended sustain (loss and emptiness)
            is_final_note = current_semitone == 7
            if is_final_note:
                # Slow fade to nothing
                fade = max(0, 1.0 - (note_time / note_duration) * 0.5)
                amplitude *= fade

            return mix * amplitude * 0.4

        return self._create_sound_buffer(total_duration, gen)

    def _generate_signature_themes(self) -> None:
        """Generate all signature music themes."""
        # Main title theme
        self.sounds['theme_neon_dead'] = self._synth_neon_dead_theme()

        # Maya's theme (multiple variations for different transformation stages)
        self.sounds['theme_maya_human'] = self._synth_half_alive_theme(dissonance_level=0.0)
        self.sounds['theme_maya_turning'] = self._synth_half_alive_theme(dissonance_level=0.3)
        self.sounds['theme_maya_lost'] = self._synth_half_alive_theme(dissonance_level=0.7)
        self.sounds['theme_maya_zombie'] = self._synth_half_alive_theme(dissonance_level=1.0)

        # Danger theme (multiple variations for different proximity/health states)
        self.sounds['theme_hunger_distant'] = self._synth_the_hunger_theme(proximity=0.2, health_ratio=1.0)
        self.sounds['theme_hunger_near'] = self._synth_the_hunger_theme(proximity=0.5, health_ratio=0.7)
        self.sounds['theme_hunger_critical'] = self._synth_the_hunger_theme(proximity=0.8, health_ratio=0.3)
        self.sounds['theme_hunger_dying'] = self._synth_the_hunger_theme(proximity=1.0, health_ratio=0.1)

        # Victory theme
        self.sounds['theme_encore'] = self._synth_encore_theme()

        # Tragedy theme
        self.sounds['theme_empty_stage'] = self._synth_empty_stage_theme()

    # ==================== ZOMBIE AUDIO PERSONAS ====================

    def _synth_zombie_remembering(self, zombie_type: str, music_intensity: float = 0.5) -> Optional[pygame.mixer.Sound]:
        """Zombie 'remembering' sound - musical response to familiar music.

        Args:
            zombie_type: Type of zombie (scene, bouncer, rocker, dj)
            music_intensity: How strongly they remember (0.0-1.0)

        When zombies hear music they loved in life, they have moments of
        recognition - producing more musical, less aggressive vocalizations.
        """
        # Musical pitch ranges per zombie type (higher = more melodic)
        melodic_ranges = {
            'scene': (165, 220),    # Mid melodic range
            'bouncer': (110, 165),  # Lower, but still melodic
            'rocker': (220, 330),   # Higher, passionate
            'dj': (165, 247),       # Musical, rhythmic
        }

        low_freq, high_freq = melodic_ranges.get(zombie_type, (165, 220))

        envelope = ADSR(attack=0.15, decay=0.2, sustain=0.8, release=0.4)

        def gen(t, dur):
            # More melodic progression when remembering
            # Simple major triad (root-third-fifth)
            beat_duration = 0.6
            beat = int(t / beat_duration) % 3
            semitone_offsets = [0, 4, 7]  # Major triad
            semitone = semitone_offsets[beat]

            freq = low_freq * (2 ** (semitone / 12.0))

            # Human-like tone (more sine, less noise)
            human_ratio = music_intensity
            zombie_ratio = 1.0 - music_intensity

            # Layer 1: Pure melodic tone (the memory)
            melody = WaveformGenerator.sine(freq, t) * 0.5 * human_ratio

            # Layer 2: Harmonic (musical quality)
            harmonic = WaveformGenerator.sine(freq * 1.5, t) * 0.3 * human_ratio

            # Layer 3: Zombie groan remnant (fading)
            groan = WaveformGenerator.sawtooth(freq * 0.7, t) * 0.4 * zombie_ratio

            # Layer 4: Gentle vibrato (emotion)
            vibrato_mod = 1.0 + 0.05 * math.sin(t * 5) * human_ratio

            # Layer 5: Residual rasp (still partially zombie)
            rasp = WaveformGenerator.noise(int(t * 800)) * 0.1 * zombie_ratio

            mix = (melody + harmonic + groan + rasp) * vibrato_mod

            # Apply envelope
            note_time = (t % beat_duration)
            amplitude = envelope.get_amplitude(note_time, beat_duration)

            return mix * amplitude * 0.5

        return self._create_sound_buffer(1.8, gen)

    def _synth_zombie_pacified(self, zombie_type: str) -> Optional[pygame.mixer.Sound]:
        """Zombie pacified/calmed by music - peaceful vocalization."""
        envelope = ADSR(attack=0.2, decay=0.3, sustain=0.7, release=0.6)

        def gen(t, dur):
            # Peaceful, descending pitch (relaxation)
            progress = t / dur
            base_freq = 150 - 50 * progress  # Descending pitch = calming

            # Soft sine wave (peaceful)
            peaceful = WaveformGenerator.sine(base_freq, t) * 0.6

            # Gentle harmonic
            harmonic = WaveformGenerator.sine(base_freq * 1.5, t) * 0.3

            # Minimal rasp (humanity returning)
            rasp = WaveformGenerator.noise(int(t * 500)) * 0.1

            mix = peaceful + harmonic + rasp
            return mix * envelope.get_amplitude(t, dur) * 0.4

        return self._create_sound_buffer(1.5, gen)

    def _synth_zombie_death(self, zombie_type: str) -> Optional[pygame.mixer.Sound]:
        """Zombie death/final release sound."""
        envelope = ADSR(attack=0.1, decay=0.4, sustain=0.5, release=1.0)

        # Different death sounds per type
        pitch_ranges = {
            'scene': (120, 60),     # Mid to low
            'bouncer': (100, 50),   # Low to very low
            'rocker': (150, 70),    # Higher to mid
            'dj': (130, 65),        # Mid to low-mid
        }

        high_freq, low_freq = pitch_ranges.get(zombie_type, (120, 60))

        def gen(t, dur):
            # Descending pitch (life fading)
            progress = t / dur
            freq = high_freq - (high_freq - low_freq) * progress

            # Final groan
            groan = WaveformGenerator.sine(freq, t) * 0.5

            # Gurgling texture
            gurgle_freq = freq + 20 * math.sin(t * 15)
            gurgle = WaveformGenerator.sawtooth(gurgle_freq, t) * 0.3

            # Final breath (noise)
            breath = WaveformGenerator.noise(int(t * 2000)) * (0.2 * progress)

            mix = groan + gurgle + breath
            return mix * envelope.get_amplitude(t, dur) * 0.5

        return self._create_sound_buffer(2.0, gen)

    # ==================== AMBIENT SOUNDSCAPES ====================

    def _generate_ambient_soundscapes(self) -> None:
        """Generate ambient soundscapes for each room."""
        # Hennepin Outside - street ambience
        self.ambience_sounds['hennepin_outside'] = self._synth_street_ambience()

        # Record Store - muffled music and crowd
        self.ambience_sounds['record_store'] = self._synth_record_store_ambience()

        # College Radio - electrical hum and equipment
        self.ambience_sounds['college_station'] = self._synth_radio_station_ambience()

        # Backstage - equipment buzz and distant music
        self.ambience_sounds['backstage_stage'] = self._synth_backstage_ambience()

        # Green Room - ventilation and muffled sounds
        self.ambience_sounds['green_room'] = self._synth_green_room_ambience()

    def _synth_street_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Hennepin Avenue street atmosphere - Enhanced with variations.

        Features:
        - Distant traffic rumble (constant)
        - Wind gusts (variable)
        - Occasional sirens (danger cue)
        - Neon buzz (1982 atmosphere)
        - Distant club bass (music bleeding from venues)
        """
        def gen(t, dur):
            # Layer 1: Distant traffic rumble (low frequency drone)
            traffic_freq = 40 + 15 * math.sin(t * 0.3)  # Slow variation
            traffic = WaveformGenerator.sine(traffic_freq, t) * 0.25

            # Layer 2: Wind gusts (natural variation)
            wind_intensity = 0.8 + 0.4 * math.sin(t * 0.7)  # Gusting
            wind = WaveformGenerator.noise(int(t * 2000)) * 0.12 * wind_intensity

            # Layer 3: Occasional distant siren (danger atmosphere)
            siren_active = (t % 10.0) > 7.5
            siren = 0
            if siren_active:
                siren_freq = 600 + 250 * math.sin(t * 9)
                siren = WaveformGenerator.sine(siren_freq, t) * 0.18

            # Layer 4: Neon buzz (1982 street atmosphere)
            neon_freq = 120 + 30 * math.sin(t * 13)  # Buzzing variation
            neon = WaveformGenerator.square(neon_freq, t, duty=0.2) * 0.08

            # Layer 5: Distant club bass (muffled music from venues)
            club_pattern = math.sin(t * 2) ** 2  # 4-on-the-floor kick pattern
            club_bass = WaveformGenerator.sine(60, t) * club_pattern * 0.15

            # Layer 6: Footsteps surface - pavement (echo/reverb)
            # Subtle ambient footsteps in distance
            footstep_active = (t % 3.5) < 0.1
            distant_step = WaveformGenerator.noise(int(t * 15000)) * (0.08 if footstep_active else 0.0)

            return traffic + wind + siren + neon + club_bass + distant_step

        return self._create_sound_buffer(5.0, gen)

    def _synth_record_store_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Record store interior - Enhanced vinyl warmth and music culture.

        Features:
        - Muffled new wave bass from listening booth
        - Vinyl crackle and warmth
        - Crowd murmur and browsing sounds
        - Cash register dings
        - Record flipping sounds
        - Footsteps on wood floor
        """
        def gen(t, dur):
            # Layer 1: Muffled new wave bass from listening booth
            # Rhythmic bass pattern (new wave beat)
            bass_freq = 65 + 15 * math.sin(t * 1.8)
            bass_pattern = math.sin(t * 2.4) ** 2  # Rhythmic pulse
            bass = WaveformGenerator.sine(bass_freq, t) * bass_pattern * 0.28

            # Layer 2: Vinyl warmth - constant crackle
            vinyl_crackle = WaveformGenerator.noise(int(t * 22000)) * 0.06

            # Layer 3: Low-frequency vinyl rumble
            vinyl_rumble = WaveformGenerator.sine(30 + 5 * math.sin(t * 0.4), t) * 0.12

            # Layer 4: Crowd murmur (people browsing)
            murmur_mod = 1.0 + 0.3 * math.sin(t * 0.6)  # Conversation swells
            murmur = WaveformGenerator.noise(int(t * 600)) * 0.14 * murmur_mod

            # Layer 5: Occasional cash register ding
            register_active = (t % 7.0) < 0.05
            register = WaveformGenerator.sine(1200, t) * (0.15 if register_active else 0.0)

            # Layer 6: Record flipping sounds (every few seconds)
            flip_active = ((t + 2) % 5.0) < 0.08
            flip = WaveformGenerator.noise(int(t * 8000)) * (0.1 if flip_active else 0.0)

            # Layer 7: Wooden floor creaks (footsteps)
            creak_active = (t % 2.8) < 0.12
            creak_freq = 180 + 40 * math.sin(t * 20)
            creak = WaveformGenerator.sawtooth(creak_freq, t) * (0.08 if creak_active else 0.0)

            return bass + vinyl_crackle + vinyl_rumble + murmur + register + flip + creak

        return self._create_sound_buffer(4.0, gen)

    def _synth_radio_station_ambience(self) -> Optional[pygame.mixer.Sound]:
        """College radio station - Enhanced broadcast atmosphere.

        Features:
        - 60Hz electrical hum (AC power)
        - Equipment buzz and interference
        - Tape hiss and analog warmth
        - Microphone feedback occasional
        - DJ headphone bleed
        - Turntable motor hum
        - ON AIR light buzz
        """
        def gen(t, dur):
            # Layer 1: 60Hz electrical hum with harmonics
            hum_60 = WaveformGenerator.sine(60, t) * 0.22
            hum_120 = WaveformGenerator.sine(120, t) * 0.12
            hum_180 = WaveformGenerator.sine(180, t) * 0.06

            # Layer 2: Equipment buzz (variable)
            buzz_freq = 850 + 120 * math.sin(t * 11.5)
            buzz = WaveformGenerator.square(buzz_freq, t, duty=0.25) * 0.09

            # Layer 3: Tape hiss (analog character)
            tape_hiss = WaveformGenerator.noise(int(t * 32000)) * 0.07

            # Layer 4: Turntable motor hum
            motor = WaveformGenerator.sine(33.3, t) * 0.08  # 33⅓ RPM

            # Layer 5: Occasional microphone feedback squeal
            feedback_active = (t % 12.0) > 10.5
            feedback_freq = 1200 + 400 * math.sin(t * 25)
            feedback = WaveformGenerator.sine(feedback_freq, t) * (0.12 if feedback_active else 0.0)

            # Layer 6: DJ headphone bleed (distant muffled music)
            headphone_freq = 200 + 80 * math.sin(t * 3.2)
            headphone = WaveformGenerator.square(headphone_freq, t, duty=0.4) * 0.06

            # Layer 7: ON AIR light buzz
            onair_buzz_freq = 120 + 20 * math.sin(t * 17)
            onair_buzz = WaveformGenerator.square(onair_buzz_freq, t, duty=0.2) * 0.05

            # Layer 8: Radio static bursts
            static_active = (t % 8.5) < 0.15
            static = WaveformGenerator.noise(int(t * 25000)) * (0.1 if static_active else 0.0)

            return (hum_60 + hum_120 + hum_180 + buzz + tape_hiss + motor +
                   feedback + headphone + onair_buzz + static)

        return self._create_sound_buffer(4.5, gen)

    def _synth_backstage_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Backstage area - Enhanced pre-show energy and equipment.

        Features:
        - Amplifier buzz and hum
        - Distant muffled band (sound check bleeding through)
        - Cable interference and ground hum
        - Guitar tuning sounds
        - Drum kit rattles
        - Stage crew movement
        - Door slams and equipment movement
        """
        def gen(t, dur):
            # Layer 1: Amplifier buzz (60Hz + 120Hz ground loop)
            amp_buzz = WaveformGenerator.sine(60, t) * 0.18
            amp_buzz += WaveformGenerator.sine(120, t) * 0.12

            # Layer 2: Distant muffled drums (four-on-the-floor rock pattern)
            # Kick on 1 and 3, snare on 2 and 4
            beat_time = t % 2.0
            kick_active = beat_time < 0.12 or (beat_time > 1.0 and beat_time < 1.12)
            snare_active = (beat_time > 0.48 and beat_time < 0.58) or (beat_time > 1.48 and beat_time < 1.58)

            kick = WaveformGenerator.sine(75, t) * (0.25 if kick_active else 0.0)
            snare = WaveformGenerator.noise(int(t * 12000)) * (0.15 if snare_active else 0.0)

            # Layer 3: Muffled bass guitar (following kick pattern)
            bass_freq = 82 + 41 * (int(t / 2) % 2)  # E2 to A2 alternating
            bass = WaveformGenerator.square(bass_freq, t, duty=0.3) * 0.14

            # Layer 4: Guitar tuning (occasional)
            tuning_active = (t % 9.0) > 7.5
            tuning_freq = 330 + 20 * math.sin(t * 3)  # E4 being tuned
            tuning = WaveformGenerator.sine(tuning_freq, t) * (0.12 if tuning_active else 0.0)

            # Layer 5: Cable interference (crackles and pops)
            interference = WaveformGenerator.noise(int(t * 11000)) * 0.09

            # Layer 6: Cymbal wash (distant, occasional)
            cymbal_active = ((t + 1.5) % 8.0) < 0.3
            cymbal = WaveformGenerator.noise(int(t * 28000)) * (0.1 if cymbal_active else 0.0)

            # Layer 7: Equipment movement (cases, amps being moved)
            movement_active = (t % 6.5) < 0.2
            movement = WaveformGenerator.noise(int(t * 6000)) * (0.12 if movement_active else 0.0)

            # Layer 8: Concrete floor footsteps (stage crew)
            footstep_active = (t % 2.3) < 0.08
            footstep = WaveformGenerator.sine(100, t) * (0.1 if footstep_active else 0.0)

            return (amp_buzz + kick + snare + bass + tuning + interference +
                   cymbal + movement + footstep)

        return self._create_sound_buffer(5.0, gen)

    def _synth_green_room_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Green room - Enhanced intimate pre-show atmosphere.

        Features:
        - HVAC ventilation (constant low rumble)
        - Acoustic guitar tuning/warming up
        - Muffled conversation and band bonding
        - Footsteps above (venue activity)
        - Cassette player/boombox playing quietly
        - Lighter clicks and smoke
        - Nervous energy (tapping, pacing)
        """
        def gen(t, dur):
            # Layer 1: HVAC ventilation system
            hvac_freq = 42 + 6 * math.sin(t * 1.3)
            hvac_drone = WaveformGenerator.sine(hvac_freq, t) * 0.2
            hvac_air = WaveformGenerator.noise(int(t * 3200)) * 0.11

            # Layer 2: Acoustic guitar tuning/warming up (occasional)
            guitar_active = (t % 11.0) > 8.0
            guitar_freq = 165 + 82 * (int(t / 1.5) % 2)  # E3 to B3
            guitar_strum = WaveformGenerator.triangle(guitar_freq, t) * (0.15 if guitar_active else 0.0)

            # Layer 3: Muffled conversation (band members talking)
            conversation_intensity = 0.9 + 0.3 * math.sin(t * 0.7)  # Conversational flow
            conversation = WaveformGenerator.noise(int(t * 450)) * 0.12 * conversation_intensity

            # Layer 4: Footsteps above (venue staff, other bands)
            footstep_active = (t % 4.7) < 0.11
            footstep = WaveformGenerator.noise(int(t * 16000)) * (0.14 if footstep_active else 0.0)
            footstep += WaveformGenerator.sine(85, t) * (0.08 if footstep_active else 0.0)

            # Layer 5: Cassette/boombox playing quietly (new wave tape)
            tape_freq = 110 + 30 * math.sin(t * 2.7)
            tape_warble = 1.0 + 0.03 * math.sin(t * 0.9)  # Tape wow/flutter
            tape_music = WaveformGenerator.square(tape_freq, t, duty=0.35) * 0.08 * tape_warble
            tape_hiss = WaveformGenerator.noise(int(t * 28000)) * 0.04  # Tape hiss

            # Layer 6: Lighter clicks (nervous smoking)
            lighter_active = (t % 13.0) < 0.04
            lighter = WaveformGenerator.noise(int(t * 18000)) * (0.12 if lighter_active else 0.0)

            # Layer 7: Nervous tapping/pacing (pre-show jitters)
            tap_active = (t % 1.8) < 0.06
            tap_freq = 250 + 100 * (int(t) % 2)
            tap = WaveformGenerator.sine(tap_freq, t) * (0.07 if tap_active else 0.0)

            # Layer 8: Distant muffled stage sounds
            stage_rumble = WaveformGenerator.sine(55, t) * 0.09

            return (hvac_drone + hvac_air + guitar_strum + conversation + footstep +
                   tape_music + tape_hiss + lighter + tap + stage_rumble)

        return self._create_sound_buffer(4.5, gen)

    def update_ambience_intensity(self, danger_level: float = 0.0) -> None:
        """Dynamically adjust ambient soundscape intensity based on danger.

        Args:
            danger_level: 0.0 (safe) to 1.0 (high danger)

        When zombies are near, ambient sounds become more tense:
        - Volumes shift (some louder, some quieter)
        - Certain elements become more prominent
        - Creates unease without explicit danger sounds
        """
        if not self.initialized or not self.current_room_ambience:
            return

        # Get current ambient channel
        channel = pygame.mixer.Channel(MUSIC_CHANNELS + SFX_CHANNELS)

        # Calculate reactive volume
        # Base volume decreases slightly as danger increases (quieter to hear threats)
        # But certain frequencies become more noticeable (tension)
        base_reduction = 0.15 * danger_level
        tension_boost = 0.1 * danger_level

        # Net effect: slight reduction at high danger, but with tension
        final_volume = self.ambient_volume * self.master_volume * (1.0 - base_reduction + tension_boost)
        final_volume = max(0.2, min(1.0, final_volume))  # Clamp

        channel.set_volume(final_volume)

    # ==================== PROCEDURAL MUSIC SYSTEM ====================

    def _init_procedural_music(self) -> None:
        """Initialize procedural music layers with room-specific themes."""
        # BASS LAYER - Foundation (changes per room)
        self.music_layers.append(ProceduralMusicLayer(
            name="bass",
            base_freq=55,  # A1
            pattern=[0, 0, 7, 7, 5, 5, 7, 7],  # A-A-E-E-D-D-E-E
            waveform="sine",
            duration=8.0
        ))

        # STREET LAYER - Distant punk bass
        self.music_layers.append(ProceduralMusicLayer(
            name="street_punk",
            base_freq=82,  # E2
            pattern=[0, 0, 5, 5, 3, 3, 5, 5],  # Punk rhythm
            waveform="square",
            duration=4.0
        ))

        # RECORD STORE LAYER - New wave arpeggio
        self.music_layers.append(ProceduralMusicLayer(
            name="record_newwave",
            base_freq=220,  # A3
            pattern=[0, 4, 7, 11, 12, 11, 7, 4],  # New wave progression
            waveform="triangle",
            duration=8.0
        ))

        # RADIO STATION LAYER - Electronic synth
        self.music_layers.append(ProceduralMusicLayer(
            name="radio_electronic",
            base_freq=440,  # A4
            pattern=[0, 2, 5, 7, 9, 7, 5, 2],  # Electronic melody
            waveform="sawtooth",
            duration=6.0
        ))

        # BACKSTAGE LAYER - Raw guitar energy
        self.music_layers.append(ProceduralMusicLayer(
            name="backstage_guitar",
            base_freq=165,  # E3
            pattern=[0, 0, 7, 7, 5, 7, 10, 12],  # Rock progression
            waveform="square",
            duration=4.0
        ))

        # GREEN ROOM LAYER - Acoustic ambient
        self.music_layers.append(ProceduralMusicLayer(
            name="greenroom_ambient",
            base_freq=330,  # E4
            pattern=[0, 4, 7, 4, 0, -3, 0, 4],  # Gentle acoustic
            waveform="triangle",
            duration=10.0
        ))

        # TENSION LAYERS (universal)
        # Pulse layer - danger/tension
        self.music_layers.append(ProceduralMusicLayer(
            name="pulse",
            base_freq=110,  # A2
            pattern=[0, 0, 0, 0, 3, 3, 3, 3],  # Rhythmic pulse
            waveform="square",
            duration=4.0
        ))

        # Lead layer - chase
        self.music_layers.append(ProceduralMusicLayer(
            name="lead",
            base_freq=880,  # A5
            pattern=[0, 2, 4, 5, 7, 9, 11, 12],  # Minor scale ascent
            waveform="sawtooth",
            duration=4.0
        ))

        # Set initial tension
        self.set_music_tension(TensionLevel.EXPLORATION)

    def set_music_tension(self, tension: TensionLevel, room_id: Optional[str] = None) -> None:
        """Set music tension level with room-specific themes.

        Args:
            tension: Current tension level
            room_id: Optional room ID to customize music per location
        """
        self.current_tension = tension

        # Base volumes for all room layers (off by default)
        room_volumes = {
            'street_punk': 0.0,
            'record_newwave': 0.0,
            'radio_electronic': 0.0,
            'backstage_guitar': 0.0,
            'greenroom_ambient': 0.0,
        }

        # Activate appropriate room layer
        if room_id == 'hennepin_outside':
            # Street - Distant punk bass, city ambience
            room_volumes['street_punk'] = 0.3 if tension in [TensionLevel.SAFE, TensionLevel.EXPLORATION] else 0.2
        elif room_id == 'record_store':
            # Record Store - Lo-fi new wave, vinyl warmth
            room_volumes['record_newwave'] = 0.4 if tension in [TensionLevel.SAFE, TensionLevel.EXPLORATION] else 0.3
        elif room_id == 'college_station':
            # KJRR - Electronic/synth, radio static
            room_volumes['radio_electronic'] = 0.5 if tension in [TensionLevel.SAFE, TensionLevel.EXPLORATION] else 0.3
        elif room_id == 'backstage_stage':
            # Backstage - Raw rock energy, pre-show tension
            room_volumes['backstage_guitar'] = 0.4 if tension in [TensionLevel.SAFE, TensionLevel.EXPLORATION] else 0.3
        elif room_id == 'green_room':
            # Green Room - Acoustic intimacy, quiet moments
            room_volumes['greenroom_ambient'] = 0.4 if tension in [TensionLevel.SAFE, TensionLevel.EXPLORATION] else 0.2

        # Set tension-based layers
        if tension == TensionLevel.MENU:
            # Just bass and room ambient
            self._set_layer_volumes(
                bass=0.3,
                pulse=0.0,
                lead=0.0,
                **room_volumes
            )

        elif tension == TensionLevel.SAFE:
            # Gentle, room-specific
            self._set_layer_volumes(
                bass=0.2,
                pulse=0.0,
                lead=0.0,
                **room_volumes
            )

        elif tension == TensionLevel.EXPLORATION:
            # Normal exploration with room flavor
            self._set_layer_volumes(
                bass=0.3,
                pulse=0.1,
                lead=0.0,
                **room_volumes
            )

        elif tension == TensionLevel.DANGER:
            # Zombie detected - reduce room music, add tension
            for key in room_volumes:
                room_volumes[key] *= 0.5
            self._set_layer_volumes(
                bass=0.4,
                pulse=0.4,
                lead=0.2,
                **room_volumes
            )

        elif tension == TensionLevel.CHASE:
            # Active chase - minimal room music, max tension
            for key in room_volumes:
                room_volumes[key] *= 0.2
            self._set_layer_volumes(
                bass=0.5,
                pulse=0.6,
                lead=0.5,
                **room_volumes
            )

    def _set_layer_volumes(self, **volumes):
        """Set target volumes for named layers."""
        for layer in self.music_layers:
            if layer.name in volumes:
                layer.target_volume = volumes[layer.name]

    def update_music(self, dt: float) -> None:
        """Update procedural music (call each frame)."""
        if not self.initialized:
            return

        self.music_time += dt

        # Update layer volumes (crossfading)
        for layer in self.music_layers:
            layer.update(dt)

    # ==================== SPATIAL AUDIO ====================

    def play_spatial(self, sound_name: str, source_pos: Tuple[float, float],
                    listener_pos: Tuple[float, float], volume: float = 1.0,
                    fallback_sound: Optional[str] = None) -> None:
        """Play a sound with spatial positioning.

        Args:
            sound_name: Name of sound to play
            source_pos: (x, y) position of sound source
            listener_pos: (x, y) position of listener
            volume: Base volume
            fallback_sound: Sound to use if sound_name not found
        """
        if not self.initialized:
            return

        # Try to get the sound
        sound = self.sounds.get(sound_name)
        if not sound and fallback_sound:
            sound = self.sounds.get(fallback_sound)

        if not sound:
            return

        # Calculate distance
        distance = math.sqrt(
            (source_pos[0] - listener_pos[0])**2 +
            (source_pos[1] - listener_pos[1])**2
        )

        # Calculate pan
        left, right = self.spatial.calculate_pan(source_pos[0], listener_pos[0])

        # Calculate distance attenuation
        attenuation = self.spatial.calculate_distance_attenuation(distance)

        # Apply volumes
        final_volume = volume * self.sfx_volume * self.master_volume * attenuation

        if final_volume > 0.01:  # Only play if audible
            # Pygame doesn't support per-sound panning easily,
            # so we use volume as a proxy for distance
            sound.set_volume(final_volume)
            sound.play()

    # ==================== ROOM AMBIENCE ====================

    def set_room_ambience(self, room_id: str) -> None:
        """Set ambient sound and music theme for current room.

        Args:
            room_id: ID of the room to set ambience for
        """
        if not self.initialized:
            return

        # Stop current ambience
        if self.current_room_ambience:
            pygame.mixer.stop()

        self.current_room_ambience = room_id

        # Start new ambience
        ambience = self.ambience_sounds.get(room_id)
        if ambience:
            # Play on dedicated ambient channel with looping
            channel = pygame.mixer.Channel(MUSIC_CHANNELS + SFX_CHANNELS)
            channel.set_volume(self.ambient_volume * self.master_volume)
            channel.play(ambience, loops=-1, fade_ms=500)

        # Update music layers for room theme
        self.set_music_tension(self.current_tension, room_id)

    # ==================== SIGNATURE THEME PLAYBACK ====================

    def play_theme(self, theme: MusicTheme, volume: float = 1.0, loops: int = -1) -> None:
        """Play a signature music theme.

        Args:
            theme: The theme to play (from MusicTheme enum)
            volume: Volume multiplier (0.0-1.0)
            loops: Number of times to loop (-1 = infinite)
        """
        if not self.initialized:
            return

        # Map theme enum to sound name
        theme_sounds = {
            MusicTheme.NEON_DEAD: 'theme_neon_dead',
            MusicTheme.HALF_ALIVE: 'theme_maya_human',
            MusicTheme.THE_HUNGER: 'theme_hunger_distant',
            MusicTheme.ENCORE: 'theme_encore',
            MusicTheme.EMPTY_STAGE: 'theme_empty_stage',
        }

        sound_name = theme_sounds.get(theme)
        if sound_name and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound:
                sound.set_volume(volume * self.music_volume * self.master_volume)
                # Use dedicated music channel
                channel = pygame.mixer.Channel(0)
                channel.play(sound, loops=loops, fade_ms=500)

    def play_maya_theme(self, transformation_stage: float = 0.0, volume: float = 1.0) -> None:
        """Play Maya's theme based on her transformation stage.

        Args:
            transformation_stage: 0.0 (human) to 1.0 (full zombie)
            volume: Volume multiplier
        """
        if not self.initialized:
            return

        # Select appropriate variation
        if transformation_stage < 0.25:
            sound_name = 'theme_maya_human'
        elif transformation_stage < 0.5:
            sound_name = 'theme_maya_turning'
        elif transformation_stage < 0.75:
            sound_name = 'theme_maya_lost'
        else:
            sound_name = 'theme_maya_zombie'

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound:
                sound.set_volume(volume * self.music_volume * self.master_volume)
                channel = pygame.mixer.Channel(0)
                channel.play(sound, loops=-1, fade_ms=1000)

    def play_danger_theme(self, proximity: float = 0.0, health_ratio: float = 1.0, volume: float = 1.0) -> None:
        """Play 'The Hunger' danger theme based on proximity and health.

        Args:
            proximity: 0.0 (safe) to 1.0 (immediate danger)
            health_ratio: 1.0 (full health) to 0.0 (near death)
            volume: Volume multiplier
        """
        if not self.initialized:
            return

        # Select appropriate variation
        if proximity < 0.3 and health_ratio > 0.7:
            sound_name = 'theme_hunger_distant'
        elif proximity < 0.6 and health_ratio > 0.5:
            sound_name = 'theme_hunger_near'
        elif proximity < 0.8 or health_ratio > 0.2:
            sound_name = 'theme_hunger_critical'
        else:
            sound_name = 'theme_hunger_dying'

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound:
                # Volume increases with danger
                danger_volume = volume * (0.5 + 0.5 * proximity + 0.3 * (1.0 - health_ratio))
                sound.set_volume(danger_volume * self.music_volume * self.master_volume)
                channel = pygame.mixer.Channel(1)
                channel.play(sound, loops=-1, fade_ms=500)

    def stop_theme(self, fade_ms: int = 1000) -> None:
        """Stop all signature themes with fade out.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if not self.initialized:
            return

        # Fade out music channels
        for channel_id in range(4):  # Music channels
            channel = pygame.mixer.Channel(channel_id)
            channel.fadeout(fade_ms)

    # ==================== PLAYBACK CONTROL ====================

    def play(self, sound_name: str, volume: float = 1.0) -> None:
        """Play a sound effect."""
        if not self.initialized or sound_name not in self.sounds:
            return

        sound = self.sounds[sound_name]
        if sound:
            sound.set_volume(volume * self.sfx_volume * self.master_volume)
            sound.play()

    def play_music(self, music_name: str, loops: int = -1, fade_ms: int = 1000) -> None:
        """Start playing music (for external music files if added later)."""
        if not self.initialized:
            return
        self.current_music = music_name
        # Procedural music is always playing, this is just for compatibility

    def stop_music(self, fade_ms: int = 1000) -> None:
        """Stop the current music."""
        if not self.initialized:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception:
            pass
        self.current_music = None

    def pause_music(self) -> None:
        """Pause the current music."""
        if not self.initialized:
            return
        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except Exception:
            pass

    def resume_music(self) -> None:
        """Resume paused music."""
        if not self.initialized:
            return
        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except Exception:
            pass

    def set_master_volume(self, volume: float) -> None:
        """Set the master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float) -> None:
        """Set the music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.initialized:
            try:
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume: float) -> None:
        """Set the sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_ambient_volume(self, volume: float) -> None:
        """Set the ambient volume (0.0 to 1.0)."""
        self.ambient_volume = max(0.0, min(1.0, volume))


# Global audio manager instance
_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance."""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
