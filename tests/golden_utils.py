"""Shared golden-frame rendering: used by test_golden_frames.py and
tools/update_goldens.py so both produce byte-identical frames.

Determinism contract: painted PNG backgrounds, authored sprites, the
bundled font with antialias off, no update() ticks (zombies stay at
their JSON spawn poses), infection zero, invincibility blink disabled,
shake at rest, announce off (no typewriter text mid-animation).
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def render_room_frame(engine, room_id: str):
    """Compose one deterministic native frame for a room."""
    engine.change_room(room_id, announce=False)
    engine.hero.is_invincible = False
    engine.hero.invincibility_timer = 0.0
    engine.hero.flash_timer = 0.0
    engine.hero.infection = 0.0
    engine.message_box.full_message = ""
    engine.message_box.displayed_message = ""
    engine.draw()
    return engine.screen.copy()
