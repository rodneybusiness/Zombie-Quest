"""Tests for the native->window integer-scale presenter."""
import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from zombie_quest.config import DISPLAY
from zombie_quest.presenter import Presenter


@pytest.fixture
def presenter():
    pygame.init()
    return Presenter()


class TestScaleAndLetterbox:
    def test_default_window_is_3x_native(self, presenter):
        assert presenter.scale == DISPLAY.SCALE_FACTOR
        assert presenter.offset == (0, 0)
        assert presenter.native.get_size() == (320, 276)

    def test_resize_picks_largest_integer_scale(self, presenter):
        presenter.handle_resize((1000, 900))
        assert presenter.scale == 3
        assert presenter.offset == ((1000 - 960) // 2, (900 - 828) // 2)

    def test_resize_smaller_drops_to_2x(self, presenter):
        presenter.handle_resize((700, 600))
        assert presenter.scale == 2
        assert presenter.offset == ((700 - 640) // 2, (600 - 552) // 2)

    def test_resize_tiny_clamps_to_1x(self, presenter):
        presenter.handle_resize((200, 100))
        assert presenter.scale == 1

    def test_exact_native_size_is_1x_no_letterbox(self, presenter):
        presenter.handle_resize((320, 276))
        assert presenter.scale == 1
        assert presenter.offset == (0, 0)


class TestMouseMapping:
    def test_round_trip_all_native_corners(self, presenter):
        presenter.handle_resize((1000, 900))
        for corner in [(0, 0), (319, 0), (0, 275), (319, 275)]:
            window_point = presenter.native_to_window(corner)
            assert presenter.window_to_native(window_point) == corner

    def test_letterbox_clicks_return_none(self, presenter):
        presenter.handle_resize((1000, 900))
        assert presenter.window_to_native((0, 0)) is None
        assert presenter.window_to_native((999, 899)) is None

    def test_center_pixel_maps_within_cell(self, presenter):
        # Any window pixel inside a native cell maps to that cell.
        base = presenter.native_to_window((10, 20))
        for dx in range(presenter.scale):
            for dy in range(presenter.scale):
                assert presenter.window_to_native((base[0] + dx, base[1] + dy)) == (10, 20)


class TestPresent:
    def test_present_draws_scaled_native(self, presenter):
        presenter.native.fill((255, 20, 147))
        presenter.present()
        sample = presenter.window.get_at((10, 10))
        assert sample[:3] == (255, 20, 147)

    def test_scanlines_darken_rows_at_scale_pitch(self, presenter):
        presenter.native.fill((240, 234, 224))
        presenter.present()
        scale = presenter.scale
        bright = presenter.window.get_at((5, 0))[:3]
        dark = presenter.window.get_at((5, scale - 1))[:3]
        assert sum(dark) < sum(bright)

    def test_scanlines_can_be_disabled(self, presenter):
        presenter.scanlines_enabled = False
        presenter.native.fill((240, 234, 224))
        presenter.present()
        scale = presenter.scale
        assert presenter.window.get_at((5, scale - 1))[:3] == \
            presenter.window.get_at((5, 0))[:3]
