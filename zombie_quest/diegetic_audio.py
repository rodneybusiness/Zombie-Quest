"""Diegetic audio sources - sound that exists within the game world.

These audio sources are positioned in 3D space and affect nearby zombies.
Players can use musical items to create temporary diegetic sources that
pacify or distract zombies based on their music preferences.

Features:
- Positioned audio sources with radius of effect
- Room-specific ambient music (vinyl, radio, band practice)
- Musical items create temporary sources when used
- Zombies respond based on distance and music type
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame


@dataclass
class DiegeticSource:
    """An audio source that exists within the game world.

    Attributes:
        position: (x, y) world position of the source
        music_type: Type of music ('guitar', 'electronic', 'new_wave', etc.)
        radius: Maximum distance of effect in pixels
        intensity: Base intensity of the music (0.0-1.0)
        duration: How long the source lasts (-1 for permanent)
        description: What this source is (for debugging/feedback)
    """
    position: Tuple[float, float]
    music_type: str
    radius: float
    intensity: float
    duration: float = -1.0  # -1 means permanent
    description: str = "Audio Source"

    def get_intensity_at(self, target_pos: Tuple[float, float]) -> float:
        """Calculate intensity at a given position based on distance.

        Args:
            target_pos: (x, y) position to check

        Returns:
            Intensity at that position (0.0-1.0)
        """
        distance = math.sqrt(
            (self.position[0] - target_pos[0])**2 +
            (self.position[1] - target_pos[1])**2
        )

        if distance >= self.radius:
            return 0.0

        # Linear falloff with distance
        falloff = 1.0 - (distance / self.radius)
        return self.intensity * falloff

    def update(self, dt: float) -> bool:
        """Update the source. Returns True if still active."""
        if self.duration < 0:
            return True  # Permanent source

        self.duration -= dt
        return self.duration > 0


class DiegeticAudioManager:
    """Manages all diegetic audio sources in the game world."""

    def __init__(self):
        self.sources: List[DiegeticSource] = []
        self.room_sources: Dict[str, List[DiegeticSource]] = {}
        self._setup_room_sources()

    def _setup_room_sources(self) -> None:
        """Set up permanent audio sources for each room."""

        # HENNEPIN OUTSIDE - Distant punk bass, city ambience
        self.room_sources['hennepin_outside'] = [
            DiegeticSource(
                position=(148, 100),  # From record store door
                music_type='punk',
                radius=120.0,
                intensity=0.3,
                description="Muffled punk bass from Let It Be Records"
            ),
            DiegeticSource(
                position=(270, 110),  # From alley
                music_type='electronic',
                radius=80.0,
                intensity=0.2,
                description="Radio static from KJRR basement"
            ),
        ]

        # RECORD STORE - Lo-fi new wave, vinyl warmth
        self.room_sources['record_store'] = [
            DiegeticSource(
                position=(220, 100),  # Listening booth
                music_type='new_wave',
                radius=150.0,
                intensity=0.6,
                description="Vinyl playing in listening booth - Joy Division"
            ),
            DiegeticSource(
                position=(100, 80),  # Turntable near counter
                music_type='ambient',
                radius=100.0,
                intensity=0.4,
                description="Ambient synth from store speakers"
            ),
        ]

        # KJRR COLLEGE STATION - Electronic/synth, radio static
        self.room_sources['college_station'] = [
            DiegeticSource(
                position=(160, 100),  # Broadcast booth center
                music_type='electronic',
                radius=180.0,
                intensity=0.8,
                description="Live broadcast - electronic set"
            ),
            DiegeticSource(
                position=(240, 120),  # Record library
                music_type='new_wave',
                radius=90.0,
                intensity=0.3,
                description="Records spinning in library"
            ),
        ]

        # BACKSTAGE - Raw rock energy, pre-show tension
        self.room_sources['backstage_stage'] = [
            DiegeticSource(
                position=(100, 80),  # Stage area
                music_type='guitar',
                radius=140.0,
                intensity=0.5,
                description="Muffled band practice through walls"
            ),
            DiegeticSource(
                position=(200, 100),  # Equipment area
                music_type='punk',
                radius=100.0,
                intensity=0.4,
                description="Soundcheck bleed from main stage"
            ),
        ]

        # GREEN ROOM - Acoustic intimacy, quiet moments
        self.room_sources['green_room'] = [
            DiegeticSource(
                position=(160, 100),  # Center of room
                music_type='ambient',
                radius=120.0,
                intensity=0.5,
                description="Soft acoustic guitar tuning"
            ),
            DiegeticSource(
                position=(80, 120),  # Corner with boombox
                music_type='new_wave',
                radius=80.0,
                intensity=0.3,
                description="Cassette playing on boombox"
            ),
        ]

    def set_room(self, room_id: str) -> None:
        """Load sources for a specific room.

        Args:
            room_id: ID of the room to load sources for
        """
        # Clear temporary sources but keep permanent ones
        self.sources = []

        # Add room-specific permanent sources
        if room_id in self.room_sources:
            self.sources.extend(self.room_sources[room_id])

    def add_temporary_source(self, source: DiegeticSource) -> None:
        """Add a temporary audio source (like from using an item).

        Args:
            source: The source to add
        """
        self.sources.append(source)

    def create_item_source(self, item_name: str, position: Tuple[float, float]) -> Optional[DiegeticSource]:
        """Create a diegetic source from a musical item.

        Args:
            item_name: Name of the item being used
            position: Position to create the source at

        Returns:
            DiegeticSource if the item creates one, None otherwise
        """
        # Map items to music types and parameters
        item_configs = {
            'Guitar Pick': {
                'music_type': 'guitar',
                'radius': 120.0,
                'intensity': 0.8,
                'duration': 6.0,
                'description': 'Strumming guitar pick melody'
            },
            'Demo Tape': {
                'music_type': 'new_wave',
                'radius': 100.0,
                'intensity': 0.7,
                'duration': 8.0,
                'description': 'Demo tape playing on loop'
            },
            'Setlist': {
                'music_type': 'ambient',
                'radius': 140.0,
                'intensity': 0.6,
                'duration': 10.0,
                'description': 'Humming setlist melodies'
            },
            'Vinyl Record': {
                'music_type': 'punk',
                'radius': 130.0,
                'intensity': 0.9,
                'duration': 12.0,
                'description': 'Vinyl spinning - The Neon Dead'
            },
        }

        config = item_configs.get(item_name)
        if not config:
            return None

        return DiegeticSource(
            position=position,
            music_type=config['music_type'],
            radius=config['radius'],
            intensity=config['intensity'],
            duration=config['duration'],
            description=config['description']
        )

    def update(self, dt: float) -> None:
        """Update all sources, removing expired ones.

        Args:
            dt: Delta time in seconds
        """
        # Update sources and remove expired ones
        self.sources = [s for s in self.sources if s.update(dt)]

    def get_music_at_position(self, position: Tuple[float, float]) -> List[Tuple[str, float]]:
        """Get all music affecting a position.

        Args:
            position: (x, y) position to check

        Returns:
            List of (music_type, intensity) tuples for all sources affecting this position
        """
        music_effects = []

        for source in self.sources:
            intensity = source.get_intensity_at(position)
            if intensity > 0.05:  # Only include audible sources
                music_effects.append((source.music_type, intensity))

        return music_effects

    def get_strongest_music_at(self, position: Tuple[float, float]) -> Optional[Tuple[str, float]]:
        """Get the strongest music type affecting a position.

        Args:
            position: (x, y) position to check

        Returns:
            (music_type, intensity) for strongest source, or None if no music
        """
        effects = self.get_music_at_position(position)
        if not effects:
            return None

        # Return the strongest effect
        return max(effects, key=lambda x: x[1])

    def draw_debug(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Draw debug visualization of audio sources.

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling rooms
        """
        for source in self.sources:
            # Draw radius circle
            center = (
                int(source.position[0] - camera_offset[0]),
                int(source.position[1] - camera_offset[1])
            )

            # Color by music type
            color_map = {
                'guitar': (255, 100, 100),      # Red
                'electronic': (100, 100, 255),  # Blue
                'new_wave': (255, 100, 255),    # Magenta
                'punk': (100, 255, 100),        # Green
                'ambient': (200, 200, 100),     # Yellow
            }
            color = color_map.get(source.music_type, (150, 150, 150))

            # Draw outer radius
            try:
                pygame.draw.circle(surface, color, center, int(source.radius), 1)
                # Draw center point
                pygame.draw.circle(surface, color, center, 3)
            except (ValueError, TypeError):
                pass  # Skip if position is off-screen


# Global instance
_diegetic_audio: Optional[DiegeticAudioManager] = None


def get_diegetic_audio() -> DiegeticAudioManager:
    """Get the global diegetic audio manager instance."""
    global _diegetic_audio
    if _diegetic_audio is None:
        _diegetic_audio = DiegeticAudioManager()
    return _diegetic_audio
