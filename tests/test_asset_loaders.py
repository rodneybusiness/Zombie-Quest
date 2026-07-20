"""Tests for the PNG asset pipeline loaders (resources.py)."""
import json
import os
import shutil

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from zombie_quest.palette import ZQ32, PaletteError
from zombie_quest.resources import load_character_set, load_image, load_room_assets

ROOM_SIZE = (320, 200)


def _save_room_bg(assets_root, room_id, color, size=ROOM_SIZE):
    room_dir = os.path.join(assets_root, "rooms", room_id)
    os.makedirs(room_dir, exist_ok=True)
    surface = pygame.Surface(size)
    surface.fill(color)
    pygame.image.save(surface, os.path.join(room_dir, "bg.png"))
    return room_dir


class TestRoomAssetLoading:
    def test_missing_room_returns_none(self, tmp_path):
        assert load_room_assets(str(tmp_path), "nowhere") is None

    def test_bg_round_trip(self, tmp_path):
        _save_room_bg(str(tmp_path), "test_room", ZQ32[4])
        assets = load_room_assets(str(tmp_path), "test_room")
        assert assets is not None
        assert assets.background.get_size() == ROOM_SIZE
        assert assets.background.get_at((10, 10))[:3] == ZQ32[4]
        assert assets.priority_mask is None
        assert assets.emissive is None

    def test_priority_mask_loaded_when_present(self, tmp_path):
        room_dir = _save_room_bg(str(tmp_path), "test_room", ZQ32[4])
        mask = pygame.Surface(ROOM_SIZE)
        mask.fill((0, 0, 0))
        mask.fill((255, 255, 255), (0, 0, 50, 50))
        pygame.image.save(mask, os.path.join(room_dir, "priority.png"))
        assets = load_room_assets(str(tmp_path), "test_room")
        assert assets.priority_mask is not None
        assert assets.priority_mask.get_at((10, 10))[:3] == (255, 255, 255)
        assert assets.priority_mask.get_at((100, 100))[:3] == (0, 0, 0)

    def test_off_palette_bg_rejected(self, tmp_path):
        _save_room_bg(str(tmp_path), "bad_room", (123, 45, 67))
        with pytest.raises(PaletteError):
            load_room_assets(str(tmp_path), "bad_room")

    def test_wrong_size_rejected(self, tmp_path):
        _save_room_bg(str(tmp_path), "small_room", ZQ32[4], size=(100, 80))
        with pytest.raises(ValueError):
            load_room_assets(str(tmp_path), "small_room")


class TestCharacterSetLoading:
    def _write_character(self, assets_root, name="testchar",
                         frame_size=(16, 32), directions=("down", "up")):
        char_dir = os.path.join(assets_root, "characters", name)
        os.makedirs(char_dir, exist_ok=True)
        frame_w, frame_h = frame_size
        frames_per_direction = 3
        sheet = pygame.Surface((frame_w * frames_per_direction,
                                frame_h * len(directions)), pygame.SRCALPHA)
        # Give every frame a distinct palette color for slice verification.
        for row in range(len(directions)):
            for col in range(frames_per_direction):
                sheet.fill((*ZQ32[row * 3 + col + 1], 255),
                           (col * frame_w, row * frame_h, frame_w, frame_h))
        pygame.image.save(sheet, os.path.join(char_dir, "sheet.png"))
        meta = {
            "frame_size": list(frame_size),
            "anchor": [frame_w // 2, frame_h - 1],
            "directions": list(directions),
            "animations": {"walk": {"frames": [0, 1, 2], "fps": 6.667}},
            "perspective_steps": [0.75, 1.0, 1.25],
        }
        with open(os.path.join(char_dir, "meta.json"), "w") as handle:
            json.dump(meta, handle)
        return char_dir

    def test_missing_character_returns_none(self, tmp_path):
        assert load_character_set(str(tmp_path), "nobody") is None

    def test_sheet_slicing_round_trip(self, tmp_path):
        self._write_character(str(tmp_path))
        charset = load_character_set(str(tmp_path), "testchar")
        assert charset is not None
        assert set(charset.animations.keys()) == {"down", "up"}
        assert all(len(frames) == 3 for frames in charset.animations.values())
        assert charset.animations["down"][0].get_size() == (16, 32)
        # Frame (row 0, col 1) carries ZQ32[2]; frame (row 1, col 0) ZQ32[4].
        assert charset.animations["down"][1].get_at((5, 5))[:3] == ZQ32[2]
        assert charset.animations["up"][0].get_at((5, 5))[:3] == ZQ32[4]

    def test_meta_fields_parsed(self, tmp_path):
        self._write_character(str(tmp_path))
        charset = load_character_set(str(tmp_path), "testchar")
        assert charset.frame_size == (16, 32)
        assert charset.anchor == (8, 31)
        assert charset.perspective_steps == (0.75, 1.0, 1.25)
        assert charset.animation_map["walk"]["frames"] == [0, 1, 2]


class TestEngineRoomOverride:
    def test_asset_bg_overrides_procedural(self, tmp_path):
        """Dropping bg.png into assets/rooms/<id>/ flips that room to
        painted art and re-derives the walk-behind overlay from it."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.symlink(os.path.join(repo_root, "game_data.json"),
                   os.path.join(tmp_path, "game_data.json"))
        _save_room_bg(str(tmp_path / "assets"), "hennepin_outside", ZQ32[9])

        from zombie_quest.engine import GameEngine
        engine = GameEngine(str(tmp_path))
        room = engine.rooms["hennepin_outside"]
        assert room.background.get_at((160, 100))[:3] == ZQ32[9]
        # Overlay must be derived from the painted background now.
        mask = room.priority_mask
        for x in range(0, 320, 13):
            for y in range(0, 200, 13):
                m = mask.get_at((x, y))
                if m[0] > 200 and m[1] > 200 and m[2] > 200:
                    assert room.priority_overlay.get_at((x, y))[:3] == ZQ32[9]
        # Other rooms still use the procedural fallback path.
        assert engine.rooms["record_store"].background is not None
