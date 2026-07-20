"""Tests for the ZQ-32 palette contract and dither helpers."""
import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from zombie_quest import palette
from zombie_quest.dither import BAYER_2X2, dim_overlay, dither_fill, dither_gradient_vertical
from zombie_quest.palette import (
    RAMPS,
    ZQ32,
    BLACK,
    WHITE,
    PaletteError,
    apply_lut,
    assert_surface_palette,
    make_lut,
    nearest,
    quantize_surface,
    surface_colors,
    swatch_sheet,
    write_gpl,
)


class TestPaletteStructure:
    def test_32_unique_colors(self):
        assert len(ZQ32) == 32
        assert len(set(ZQ32)) == 32

    def test_eight_ramps_of_four(self):
        assert len(RAMPS) == 8
        for colors in RAMPS.values():
            assert len(colors) == 4

    def test_ramps_go_dark_to_light(self):
        for name, colors in RAMPS.items():
            luminances = [r * 0.299 + g * 0.587 + b * 0.114 for r, g, b in colors]
            assert luminances == sorted(luminances), f"ramp {name} not dark->light"

    def test_black_and_white_anchors(self):
        assert BLACK == (0, 0, 0)
        assert ZQ32[0] == BLACK
        assert ZQ32[31] == WHITE

    def test_brand_colors_preserved(self):
        # The game's signature colors must survive the palette lock.
        assert (255, 20, 147) in ZQ32   # HOT_MAGENTA
        assert (255, 215, 0) in ZQ32    # NEON_GOLD
        assert (240, 234, 224) in ZQ32  # BONE_WHITE
        assert (30, 10, 60) in ZQ32     # DEEP_PURPLE


class TestEnforcement:
    def test_accepts_palette_only_surface(self):
        surface = pygame.Surface((8, 8))
        surface.fill(ZQ32[5])
        assert_surface_palette(surface)

    def test_rejects_offending_color(self):
        surface = pygame.Surface((8, 8))
        surface.fill((123, 45, 67))
        with pytest.raises(PaletteError) as excinfo:
            assert_surface_palette(surface, context="unit test")
        assert "unit test" in str(excinfo.value)

    def test_ignores_transparent_pixels(self):
        surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        surface.fill((123, 45, 67, 0))
        surface.set_at((0, 0), (*ZQ32[3], 255))
        assert_surface_palette(surface)

    def test_surface_colors_lists_unique(self):
        surface = pygame.Surface((4, 4))
        surface.fill(ZQ32[1])
        surface.set_at((2, 2), ZQ32[9])
        colors = surface_colors(surface)
        assert set(colors) == {ZQ32[1], ZQ32[9]}


class TestNearestAndQuantize:
    def test_nearest_idempotent_on_members(self):
        for color in ZQ32:
            assert nearest(color) == color

    def test_nearest_snaps_off_palette(self):
        snapped = nearest((250, 25, 150))
        assert snapped == (255, 20, 147)

    def test_quantize_produces_conformant_surface(self):
        surface = pygame.Surface((6, 6))
        surface.fill((200, 100, 50))
        assert_surface_palette(quantize_surface(surface))


class TestLut:
    def test_lut_rejects_non_palette_source(self):
        with pytest.raises(PaletteError):
            make_lut({(1, 2, 3): ZQ32[0]})

    def test_lut_rejects_non_palette_target(self):
        with pytest.raises(PaletteError):
            make_lut({ZQ32[0]: (1, 2, 3)})

    def test_apply_lut_remaps_in_place(self):
        surface = pygame.Surface((4, 4))
        surface.fill(ZQ32[2])
        apply_lut(surface, make_lut({ZQ32[2]: ZQ32[7]}))
        assert surface.get_at((1, 1))[:3] == ZQ32[7]
        assert_surface_palette(surface)

    def test_apply_lut_identity_for_unmapped(self):
        surface = pygame.Surface((2, 2))
        surface.fill(ZQ32[4])
        apply_lut(surface, make_lut({ZQ32[9]: ZQ32[10]}))
        assert surface.get_at((0, 0))[:3] == ZQ32[4]


class TestDither:
    def test_dither_fill_uses_only_two_colors(self):
        surface = pygame.Surface((16, 16))
        dither_fill(surface, surface.get_rect(), ZQ32[1], ZQ32[2], mix=0.5)
        assert set(surface_colors(surface)) <= {ZQ32[1], ZQ32[2]}

    def test_dither_gradient_stays_in_ramp(self):
        surface = pygame.Surface((16, 32))
        ramp_colors = RAMPS["night"]
        dither_gradient_vertical(surface, surface.get_rect(), ramp_colors)
        assert set(surface_colors(surface)) <= set(ramp_colors)

    def test_dim_overlay_is_palette_safe(self):
        overlay = dim_overlay((8, 8), color=BLACK, coverage=0.5, matrix=BAYER_2X2)
        opaque = [overlay.get_at((x, y)) for x in range(8) for y in range(8)
                  if overlay.get_at((x, y))[3] != 0]
        assert opaque and all(p[:3] == BLACK for p in opaque)
        # 2x2 Bayer at 50% coverage darkens exactly half the pixels.
        assert len(opaque) == 32


class TestExports:
    def test_swatch_sheet_shape_and_palette(self):
        sheet = swatch_sheet(cell=4)
        assert sheet.get_size() == (16, 32)
        assert_surface_palette(sheet)

    def test_write_gpl_round_trip(self, tmp_path):
        path = tmp_path / "zq32.gpl"
        write_gpl(str(path))
        lines = [l for l in path.read_text().splitlines()
                 if l and not l.startswith(("GIMP", "Name", "Columns", "#"))]
        parsed = [tuple(int(v) for v in line.split()[:3]) for line in lines]
        assert tuple(parsed) == ZQ32
