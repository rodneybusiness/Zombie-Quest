"""Audio system - music, sound effects, and ambient audio."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional
import math

# Pygame mixer import with fallback for headless mode
try:
    import pygame.mixer
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

from .config import AUDIO


@dataclass
class SoundEffect:
    """Represents a sound effect with metadata."""
    name: str
    volume: float = 1.0
    pitch_variation: float = 0.0


class AudioManager:
    """Manages all game audio - music, SFX, and ambient sounds."""

    def __init__(self) -> None:
        self.initialized = False
        self.music_volume = AUDIO.MUSIC_VOLUME
        self.sfx_volume = AUDIO.SFX_VOLUME
        self.master_volume = AUDIO.MASTER_VOLUME

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        self.music_paused = False

        # Synthesize sounds since we don't have audio files
        self._init_synthesized_sounds()

    def _init_synthesized_sounds(self) -> None:
        """Initialize synthesized sound effects."""
        if not AUDIO_AVAILABLE:
            return

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.initialized = True
        except Exception:
            self.initialized = False
            return

        # Generate synthesized sounds
        self.sounds = {
            "footstep": self._synth_footstep(),
            "pickup": self._synth_pickup(),
            "door": self._synth_door(),
            "hit": self._synth_hit(),
            "zombie_groan": self._synth_zombie_groan(),
            "ui_click": self._synth_ui_click(),
            "ui_select": self._synth_ui_select(),
            "message": self._synth_message(),
            "success": self._synth_success(),
            "error": self._synth_error(),
        }

    def _create_sound_buffer(self, duration: float, generator) -> 'pygame.mixer.Sound':
        """Create a sound from a generator function."""
        if not self.initialized:
            return None

        import array
        sample_rate = 22050
        num_samples = int(sample_rate * duration)

        # Generate samples
        samples = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            samples[i] = int(generator(t, duration) * 32767 * 0.5)

        # Create sound from samples
        sound = pygame.mixer.Sound(buffer=samples)
        return sound

    def _synth_footstep(self) -> 'pygame.mixer.Sound':
        """Generate footstep sound."""
        def gen(t, dur):
            freq = 80 + 40 * math.sin(t * 100)
            envelope = max(0, 1 - t / dur) ** 3
            noise = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.3
            return (math.sin(t * freq * 2 * math.pi) * 0.7 + noise) * envelope
        return self._create_sound_buffer(0.1, gen)

    def _synth_pickup(self) -> 'pygame.mixer.Sound':
        """Generate item pickup sound (sparkly)."""
        def gen(t, dur):
            freq = 800 + 400 * t / dur
            envelope = max(0, 1 - t / dur) ** 0.5
            return math.sin(t * freq * 2 * math.pi) * envelope
        return self._create_sound_buffer(0.3, gen)

    def _synth_door(self) -> 'pygame.mixer.Sound':
        """Generate door transition sound."""
        def gen(t, dur):
            freq = 100 + 50 * (1 - t / dur)
            envelope = min(1, t * 10) * max(0, 1 - t / dur)
            return math.sin(t * freq * 2 * math.pi) * envelope
        return self._create_sound_buffer(0.4, gen)

    def _synth_hit(self) -> 'pygame.mixer.Sound':
        """Generate damage hit sound."""
        def gen(t, dur):
            freq = 200 - 150 * t / dur
            envelope = max(0, 1 - t / dur) ** 2
            noise = (hash(int(t * 10000)) % 1000 / 500 - 1) * 0.5
            return (math.sin(t * freq * 2 * math.pi) * 0.5 + noise) * envelope
        return self._create_sound_buffer(0.2, gen)

    def _synth_zombie_groan(self) -> 'pygame.mixer.Sound':
        """Generate zombie groan sound."""
        def gen(t, dur):
            freq = 80 + 30 * math.sin(t * 3)
            envelope = math.sin(t / dur * math.pi)
            return math.sin(t * freq * 2 * math.pi) * envelope * 0.6
        return self._create_sound_buffer(0.8, gen)

    def _synth_ui_click(self) -> 'pygame.mixer.Sound':
        """Generate UI click sound."""
        def gen(t, dur):
            freq = 1000
            envelope = max(0, 1 - t / dur) ** 4
            return math.sin(t * freq * 2 * math.pi) * envelope
        return self._create_sound_buffer(0.05, gen)

    def _synth_ui_select(self) -> 'pygame.mixer.Sound':
        """Generate UI select sound."""
        def gen(t, dur):
            freq = 600 + 200 * t / dur
            envelope = max(0, 1 - t / dur) ** 2
            return math.sin(t * freq * 2 * math.pi) * envelope
        return self._create_sound_buffer(0.15, gen)

    def _synth_message(self) -> 'pygame.mixer.Sound':
        """Generate message appear sound."""
        def gen(t, dur):
            freq = 400 + 100 * t / dur
            envelope = max(0, 1 - t / dur)
            return math.sin(t * freq * 2 * math.pi) * envelope * 0.4
        return self._create_sound_buffer(0.1, gen)

    def _synth_success(self) -> 'pygame.mixer.Sound':
        """Generate success/unlock sound."""
        def gen(t, dur):
            # Rising arpeggio
            if t < dur / 3:
                freq = 400
            elif t < dur * 2 / 3:
                freq = 500
            else:
                freq = 600
            envelope = min(1, (dur - t) / (dur * 0.3))
            return math.sin(t * freq * 2 * math.pi) * envelope
        return self._create_sound_buffer(0.4, gen)

    def _synth_error(self) -> 'pygame.mixer.Sound':
        """Generate error/fail sound."""
        def gen(t, dur):
            freq = 200 - 50 * t / dur
            envelope = max(0, 1 - t / dur)
            return math.sin(t * freq * 2 * math.pi) * envelope * 0.7
        return self._create_sound_buffer(0.3, gen)

    def play(self, sound_name: str, volume: float = 1.0) -> None:
        """Play a sound effect."""
        if not self.initialized or sound_name not in self.sounds:
            return

        sound = self.sounds[sound_name]
        if sound:
            sound.set_volume(volume * self.sfx_volume * self.master_volume)
            sound.play()

    def play_music(self, music_name: str, loops: int = -1, fade_ms: int = 1000) -> None:
        """Start playing music (placeholder - we generate ambient tones)."""
        if not self.initialized:
            return
        # In a full implementation, this would load and play music files
        self.current_music = music_name

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


# Global audio manager instance
_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance."""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
