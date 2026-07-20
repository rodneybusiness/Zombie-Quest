"""Golden-frame regression tests: every room's composed native frame
must match tests/golden/<room>.png byte-for-byte.

On mismatch, expected/actual/diff PNGs are written to build/golden_diff/
(uploaded as a CI artifact). For intentional visual changes, regenerate
with `python tools/update_goldens.py` and commit the new goldens.
"""
import os
import sys

import pygame
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from golden_utils import GOLDEN_DIR, render_room_frame

DIFF_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "golden_diff")

ROOM_IDS = [
    "hennepin_outside", "record_store", "college_station", "backstage_stage",
    "green_room", "practice_space", "club_bathroom", "record_vault",
    "promoter_office", "loading_dock",
]


@pytest.fixture(scope="module")
def engine():
    from zombie_quest.engine import GameEngine
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return GameEngine(repo_root)


@pytest.mark.parametrize("room_id", ROOM_IDS)
def test_room_frame_matches_golden(engine, room_id):
    golden_path = os.path.join(GOLDEN_DIR, f"{room_id}.png")
    assert os.path.exists(golden_path), (
        f"missing golden for {room_id}; run tools/update_goldens.py")

    actual = render_room_frame(engine, room_id)
    expected = pygame.image.load(golden_path)

    assert actual.get_size() == expected.get_size()
    actual_bytes = pygame.image.tobytes(actual, "RGB")
    expected_bytes = pygame.image.tobytes(expected, "RGB")
    if actual_bytes != expected_bytes:
        os.makedirs(DIFF_DIR, exist_ok=True)
        pygame.image.save(expected, os.path.join(DIFF_DIR, f"{room_id}_expected.png"))
        pygame.image.save(actual, os.path.join(DIFF_DIR, f"{room_id}_actual.png"))
        diff = pygame.Surface(actual.get_size())
        for x in range(0, actual.get_width(), 2):
            for y in range(0, actual.get_height(), 2):
                if actual.get_at((x, y)) != expected.get_at((x, y)):
                    diff.fill((255, 20, 147), (x, y, 2, 2))
        pygame.image.save(diff, os.path.join(DIFF_DIR, f"{room_id}_diff.png"))
        pytest.fail(
            f"{room_id} frame deviates from golden; see build/golden_diff/. "
            "If intentional, run tools/update_goldens.py and commit.")
