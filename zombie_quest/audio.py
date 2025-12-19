"""Atmospheric audio system - 1982 Minneapolis soundscape.

Advanced features:
- Layered waveform synthesis with ADSR envelopes
- Procedural music with tension-based layering
- Spatial audio with stereo panning and distance attenuation
- Dynamic zombie vocalizations with pitch variation
- Room-specific ambient soundscapes
- Event-driven audio architecture
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

        # Generic zombie sounds (fallbacks)
        self.sounds['zombie_groan'] = self._synth_zombie_groan('scene')
        self.sounds['zombie_alert'] = self._synth_zombie_alert('scene')

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
        """Hennepin Avenue street atmosphere."""
        def gen(t, dur):
            # Distant traffic rumble
            traffic = WaveformGenerator.sine(40 + 20 * math.sin(t * 0.5), t) * 0.2

            # Wind
            wind = WaveformGenerator.noise(int(t * 2000)) * 0.1 * (1 + 0.3 * math.sin(t * 0.8))

            # Occasional distant siren
            siren_active = (t % 8.0) > 6.0
            siren = 0
            if siren_active:
                siren_freq = 600 + 200 * math.sin(t * 8)
                siren = WaveformGenerator.sine(siren_freq, t) * 0.15

            return traffic + wind + siren

        return self._create_sound_buffer(4.0, gen)

    def _synth_record_store_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Record store interior - muffled bass and crowd murmur."""
        def gen(t, dur):
            # Muffled bass throb (like music from another room)
            bass = WaveformGenerator.sine(60 + 10 * math.sin(t * 2), t) * 0.25

            # Crowd murmur (low frequency noise)
            murmur = WaveformGenerator.noise(int(t * 500)) * 0.12

            # Vinyl crackle
            crackle = WaveformGenerator.noise(int(t * 20000)) * 0.05

            return bass + murmur + crackle

        return self._create_sound_buffer(3.0, gen)

    def _synth_radio_station_ambience(self) -> Optional[pygame.mixer.Sound]:
        """College radio station - electrical equipment."""
        def gen(t, dur):
            # 60Hz electrical hum
            hum = WaveformGenerator.sine(60, t) * 0.2
            hum += WaveformGenerator.sine(120, t) * 0.1

            # Equipment buzz
            buzz_freq = 800 + 100 * math.sin(t * 11)
            buzz = WaveformGenerator.square(buzz_freq, t, duty=0.3) * 0.08

            # Tape hiss
            hiss = WaveformGenerator.noise(int(t * 30000)) * 0.06

            return hum + buzz + hiss

        return self._create_sound_buffer(3.0, gen)

    def _synth_backstage_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Backstage area - equipment and distant music."""
        def gen(t, dur):
            # Equipment buzz
            buzz = WaveformGenerator.sine(120, t) * 0.15

            # Distant muffled drums (kick pattern)
            kick_pattern = 1.0 if (t % 2.0) < 0.1 or ((t + 0.5) % 2.0) < 0.1 else 0.0
            kick = WaveformGenerator.sine(80, t) * kick_pattern * 0.2

            # Cable interference
            interference = WaveformGenerator.noise(int(t * 10000)) * 0.08

            return buzz + kick + interference

        return self._create_sound_buffer(4.0, gen)

    def _synth_green_room_ambience(self) -> Optional[pygame.mixer.Sound]:
        """Green room - HVAC and muffled sounds."""
        def gen(t, dur):
            # HVAC ventilation
            hvac = WaveformGenerator.sine(40 + 5 * math.sin(t * 1.2), t) * 0.18
            hvac += WaveformGenerator.noise(int(t * 3000)) * 0.1

            # Distant muffled conversation (low murmur)
            conversation = WaveformGenerator.noise(int(t * 400)) * 0.08

            # Occasional footsteps above (if multi-story)
            footstep = 0
            if (t % 5.0) < 0.1:
                footstep = WaveformGenerator.noise(int(t * 15000)) * 0.15

            return hvac + conversation + footstep

        return self._create_sound_buffer(3.5, gen)

    # ==================== PROCEDURAL MUSIC SYSTEM ====================

    def _init_procedural_music(self) -> None:
        """Initialize procedural music layers."""
        # Base layer - always playing softly
        self.music_layers.append(ProceduralMusicLayer(
            name="bass",
            base_freq=55,  # A1
            pattern=[0, 0, 7, 7, 5, 5, 7, 7],  # A-A-E-E-D-D-E-E
            waveform="sine",
            duration=8.0
        ))

        # Arpeggio layer - exploration
        self.music_layers.append(ProceduralMusicLayer(
            name="arpeggio",
            base_freq=220,  # A3
            pattern=[0, 4, 7, 12, 7, 4, 0, -5],  # Amin arpeggio
            waveform="triangle",
            duration=8.0
        ))

        # Pad layer - ambient
        self.music_layers.append(ProceduralMusicLayer(
            name="pad",
            base_freq=440,  # A4
            pattern=[0, 0, 0, 0, 5, 5, 7, 7],  # Sustained chords
            waveform="sine",
            duration=8.0
        ))

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

    def set_music_tension(self, tension: TensionLevel) -> None:
        """Set music tension level (crossfades layers)."""
        self.current_tension = tension

        if tension == TensionLevel.MENU:
            # Just bass and pad
            self._set_layer_volumes(bass=0.3, arpeggio=0.0, pad=0.4, pulse=0.0, lead=0.0)

        elif tension == TensionLevel.SAFE:
            # Gentle, minimal
            self._set_layer_volumes(bass=0.2, arpeggio=0.3, pad=0.3, pulse=0.0, lead=0.0)

        elif tension == TensionLevel.EXPLORATION:
            # Normal exploration
            self._set_layer_volumes(bass=0.3, arpeggio=0.4, pad=0.2, pulse=0.1, lead=0.0)

        elif tension == TensionLevel.DANGER:
            # Zombie detected
            self._set_layer_volumes(bass=0.4, arpeggio=0.3, pad=0.1, pulse=0.4, lead=0.2)

        elif tension == TensionLevel.CHASE:
            # Active chase
            self._set_layer_volumes(bass=0.5, arpeggio=0.2, pad=0.0, pulse=0.6, lead=0.5)

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
        """Set ambient sound for current room."""
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
