"""Tests for configuration module."""
import pytest

from zombie_quest.config import DISPLAY, GAMEPLAY, ANIMATION, AUDIO, COLORS, GameState


class TestDisplayConfig:
    """Test display configuration values."""

    def test_room_dimensions(self):
        assert DISPLAY.ROOM_WIDTH == 320
        assert DISPLAY.ROOM_HEIGHT == 200

    def test_window_dimensions(self):
        assert DISPLAY.WINDOW_WIDTH == 320
        assert DISPLAY.WINDOW_HEIGHT == 276

    def test_ui_dimensions(self):
        assert DISPLAY.UI_BAR_HEIGHT == 40
        assert DISPLAY.MESSAGE_HEIGHT == 36


class TestGameplayConfig:
    """Test gameplay configuration values."""

    def test_hero_settings(self):
        assert GAMEPLAY.HERO_SPEED > 0
        assert GAMEPLAY.HERO_MAX_HEALTH > 0
        assert GAMEPLAY.HERO_INVINCIBILITY_TIME > 0

    def test_zombie_settings(self):
        assert GAMEPLAY.ZOMBIE_SPEED > 0
        assert GAMEPLAY.ZOMBIE_DETECTION_RADIUS > 0
        assert GAMEPLAY.ZOMBIE_WANDER_INTERVAL > 0


class TestAnimationConfig:
    """Test animation configuration values."""

    def test_timing_values(self):
        assert ANIMATION.FRAME_DURATION > 0
        assert ANIMATION.TRANSITION_DURATION > 0
        assert ANIMATION.MESSAGE_DISPLAY_TIME > 0


class TestAudioConfig:
    """Test audio configuration values."""

    def test_volume_ranges(self):
        assert 0.0 <= AUDIO.MASTER_VOLUME <= 1.0
        assert 0.0 <= AUDIO.MUSIC_VOLUME <= 1.0
        assert 0.0 <= AUDIO.SFX_VOLUME <= 1.0


class TestColorPalette:
    """Test color palette values."""

    def test_neon_colors_are_tuples(self):
        assert isinstance(COLORS.HOT_MAGENTA, tuple)
        assert isinstance(COLORS.NEON_GOLD, tuple)
        assert isinstance(COLORS.CYAN_GLOW, tuple)

    def test_color_values_are_valid(self):
        for color in [COLORS.HOT_MAGENTA, COLORS.NEON_GOLD, COLORS.CYAN_GLOW]:
            assert len(color) == 3
            for component in color:
                assert 0 <= component <= 255


class TestGameState:
    """Test game state enumeration."""

    def test_game_states_exist(self):
        assert hasattr(GameState, 'PLAYING')
        assert hasattr(GameState, 'PAUSED')
        assert hasattr(GameState, 'DIALOGUE')
        assert hasattr(GameState, 'GAME_OVER')
