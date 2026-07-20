#!/usr/bin/env python
"""Validate everything under assets/ against the ZQ-32 contract.

Checks (per file where applicable):
- rooms/<id>/bg.png        : exactly 320x200, colors subset of ZQ-32
- rooms/<id>/priority.png  : exactly 320x200, strictly binary black/white
- rooms/<id>/emissive.png  : exactly 320x200, colors subset of ZQ-32
- characters/<n>/sheet.png : palette-conformant, dimensions divisible by
                             meta.json frame_size, anchor inside frame
- fonts/*.png              : palette-conformant (plus transparent)
- palette/zq32.gpl         : byte-identical to the palette module export

Exit code 0 when clean; 1 with an error listing otherwise. Used by CI.
Run from the repo root: python tools/validate_assets.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import List, Tuple

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import pygame  # noqa: E402

from zombie_quest import palette  # noqa: E402

ROOM_SIZE = (320, 200)
REQUIRED_META_KEYS = ("frame_size", "anchor", "directions", "animations")


def _check_image(path: str, errors: List[str], expected_size: Tuple[int, int] | None,
                 palette_locked: bool = True) -> pygame.Surface | None:
    try:
        surface = pygame.image.load(path)
    except pygame.error as exc:
        errors.append(f"{path}: unreadable image ({exc})")
        return None
    if expected_size and surface.get_size() != expected_size:
        errors.append(f"{path}: size {surface.get_size()}, expected {expected_size}")
    if palette_locked:
        try:
            palette.assert_surface_palette(surface, context=path)
        except palette.PaletteError as exc:
            errors.append(str(exc))
    return surface


def _check_binary_mask(path: str, errors: List[str]) -> None:
    surface = _check_image(path, errors, ROOM_SIZE, palette_locked=False)
    if surface is None:
        return
    allowed = {(0, 0, 0), (255, 255, 255)}
    extras = [c for c in palette.surface_colors(surface, ignore_transparent=False)
              if c not in allowed]
    if extras:
        errors.append(f"{path}: priority mask must be strict black/white, found {extras[:5]}")


def _check_character(char_dir: str, errors: List[str]) -> None:
    sheet_path = os.path.join(char_dir, "sheet.png")
    meta_path = os.path.join(char_dir, "meta.json")
    if not os.path.exists(sheet_path) or not os.path.exists(meta_path):
        errors.append(f"{char_dir}: needs both sheet.png and meta.json")
        return
    sheet = _check_image(sheet_path, errors, expected_size=None)
    try:
        with open(meta_path, encoding="utf-8") as handle:
            meta = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{meta_path}: invalid JSON ({exc})")
        return
    missing = [key for key in REQUIRED_META_KEYS if key not in meta]
    if missing:
        errors.append(f"{meta_path}: missing keys {missing}")
        return
    frame_w, frame_h = meta["frame_size"]
    anchor_x, anchor_y = meta["anchor"]
    if not (0 <= anchor_x < frame_w and 0 <= anchor_y < frame_h):
        errors.append(f"{meta_path}: anchor {meta['anchor']} outside frame {meta['frame_size']}")
    if sheet is not None:
        width, height = sheet.get_size()
        if width % frame_w or height % frame_h:
            errors.append(f"{sheet_path}: {width}x{height} not divisible by frame {frame_w}x{frame_h}")
        elif height // frame_h < len(meta["directions"]):
            errors.append(f"{sheet_path}: {height // frame_h} rows < {len(meta['directions'])} directions")


def _check_gpl(assets_root: str, errors: List[str]) -> None:
    gpl_path = os.path.join(assets_root, "palette", "zq32.gpl")
    if not os.path.exists(gpl_path):
        return  # optional until the palette dir ships
    with tempfile.NamedTemporaryFile("r", suffix=".gpl", delete=False) as handle:
        temp_path = handle.name
    try:
        palette.write_gpl(temp_path)
        with open(temp_path, encoding="utf-8") as fresh, open(gpl_path, encoding="utf-8") as stored:
            if fresh.read() != stored.read():
                errors.append(f"{gpl_path}: drifted from palette.py - regenerate with palette.write_gpl")
    finally:
        os.unlink(temp_path)


def validate_all(assets_root: str) -> List[str]:
    errors: List[str] = []
    if not os.path.isdir(assets_root):
        return errors  # nothing shipped yet - vacuously clean

    rooms_root = os.path.join(assets_root, "rooms")
    if os.path.isdir(rooms_root):
        for room_id in sorted(os.listdir(rooms_root)):
            room_dir = os.path.join(rooms_root, room_id)
            if not os.path.isdir(room_dir):
                continue
            bg = os.path.join(room_dir, "bg.png")
            if os.path.exists(bg):
                _check_image(bg, errors, ROOM_SIZE)
            else:
                errors.append(f"{room_dir}: missing bg.png")
            prio = os.path.join(room_dir, "priority.png")
            if os.path.exists(prio):
                _check_binary_mask(prio, errors)
            emissive = os.path.join(room_dir, "emissive.png")
            if os.path.exists(emissive):
                _check_image(emissive, errors, ROOM_SIZE)

    chars_root = os.path.join(assets_root, "characters")
    if os.path.isdir(chars_root):
        for name in sorted(os.listdir(chars_root)):
            char_dir = os.path.join(chars_root, name)
            if os.path.isdir(char_dir):
                _check_character(char_dir, errors)

    fonts_root = os.path.join(assets_root, "fonts")
    if os.path.isdir(fonts_root):
        for name in sorted(os.listdir(fonts_root)):
            if name.endswith(".png"):
                _check_image(os.path.join(fonts_root, name), errors, expected_size=None)

    _check_gpl(assets_root, errors)
    return errors


def main() -> int:
    pygame.init()
    assets_root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "assets")
    errors = validate_all(assets_root)
    if errors:
        print(f"ASSET VALIDATION FAILED ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Asset validation clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
