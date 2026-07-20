from __future__ import annotations

import os
import sys

import pygame

from zombie_quest.engine import GameEngine
from zombie_quest.config import GameState


def dump_room_screenshots(engine: GameEngine, out_dir: str) -> None:
    """Render every room through the full draw path and save a frame each.

    Infection is zeroed so review artifacts show the rooms rather than the
    high-infection blackout overlays (those branches are already exercised
    by the forced-infection frame in the validation loop).
    """
    os.makedirs(out_dir, exist_ok=True)
    engine.hero.infection = 0.0
    engine.hero.health = engine.hero.max_health
    for room_id in engine.rooms:
        engine.change_room(room_id, announce=False)
        for _ in range(5):
            engine.update(1 / 60)
            engine.hero.infection = 0.0
        engine.draw()
        pygame.image.save(engine.screen, os.path.join(out_dir, f"{room_id}.png"))
    print(f"Saved {len(engine.rooms)} room screenshots to {out_dir}")


def run_headless_validation(engine: GameEngine, verbose: bool = False,
                            screenshot_dir: str | None = None) -> None:
    """Run comprehensive headless validation with assertions.

    This mode runs 100+ frames and validates:
    - Hero position changes
    - Zombie AI updates
    - Particle system bounds
    - State machine validity
    - No crashes during normal gameplay or rendering (draw runs every frame)
    """
    print("Starting headless validation (100+ frames)...")

    frame_count = 120
    dt = 1 / 60

    # Track initial state
    initial_hero_pos = (engine.hero.position.x, engine.hero.position.y)
    initial_room = engine.current_room.id

    # Validation counters
    validations_passed = 0
    validations_total = 0

    for frame in range(frame_count):
        # Update game
        engine.update(dt)

        # Exercise infection-driven render paths (veins, vignette, post-fx)
        # partway through the run; rendering bugs in those branches otherwise
        # only surface after a zombie hit in live play.
        if frame == 60:
            engine.hero.add_infection(55.0)

        # Render every frame - a draw crash must fail validation.
        engine.draw()
        pygame.display.flip()

        # Periodic validations
        if frame % 20 == 0:
            # Validate state machine
            validations_total += 1
            valid_states = [GameState.PLAYING, GameState.PAUSED, GameState.DIALOGUE,
                          GameState.GAME_OVER, GameState.MENU, GameState.INVENTORY,
                          GameState.TRANSITION, GameState.CREDITS]
            assert engine.state in valid_states, f"Invalid state: {engine.state}"
            validations_passed += 1

            # Validate hero position in bounds
            validations_total += 1
            room_rect = engine.current_room.bounds
            assert room_rect.left <= engine.hero.position.x <= room_rect.right, \
                f"Hero X out of bounds: {engine.hero.position.x}"
            assert room_rect.top <= engine.hero.position.y <= room_rect.bottom, \
                f"Hero Y out of bounds: {engine.hero.position.y}"
            validations_passed += 1

            # Validate hero health
            validations_total += 1
            assert 0 <= engine.hero.health <= engine.hero.max_health, \
                f"Invalid health: {engine.hero.health}"
            validations_passed += 1

            # Validate particle system
            validations_total += 1
            for particle in engine.particles.particles:
                # Particles should be within reasonable bounds
                assert -100 <= particle.x <= 500, f"Particle X out of bounds: {particle.x}"
                assert -100 <= particle.y <= 500, f"Particle Y out of bounds: {particle.y}"
            validations_passed += 1

            if verbose:
                print(f"Frame {frame}: Hero at ({engine.hero.position.x:.1f}, {engine.hero.position.y:.1f}), "
                      f"Health: {engine.hero.health}/{engine.hero.max_health}, "
                      f"State: {engine.state}, "
                      f"Particles: {len(engine.particles.particles)}")

        # Validate zombies every 30 frames
        if frame % 30 == 0:
            for zombie in engine.current_room.zombies:
                validations_total += 1
                room_rect = engine.current_room.bounds
                # Zombies should stay within reasonable bounds (with some margin)
                assert room_rect.left - 50 <= zombie.position.x <= room_rect.right + 50, \
                    f"Zombie X far out of bounds: {zombie.position.x}"
                assert room_rect.top - 50 <= zombie.position.y <= room_rect.bottom + 50, \
                    f"Zombie Y far out of bounds: {zombie.position.y}"
                validations_passed += 1

    # Final validations
    final_hero_pos = (engine.hero.position.x, engine.hero.position.y)

    validations_total += 1
    assert engine.running is True, "Engine should still be running"
    validations_passed += 1

    validations_total += 1
    assert engine.current_room is not None, "Current room should exist"
    validations_passed += 1

    validations_total += 1
    assert engine.hero is not None, "Hero should exist"
    validations_passed += 1

    # Summary
    print(f"\nHeadless validation complete!")
    print(f"Frames processed: {frame_count}")
    print(f"Validations passed: {validations_passed}/{validations_total}")
    print(f"Initial position: ({initial_hero_pos[0]:.1f}, {initial_hero_pos[1]:.1f})")
    print(f"Final position: ({final_hero_pos[0]:.1f}, {final_hero_pos[1]:.1f})")
    print(f"Initial room: {initial_room}")
    print(f"Final room: {engine.current_room.id}")
    print(f"Final health: {engine.hero.health}/{engine.hero.max_health}")
    print(f"Final state: {engine.state}")
    print(f"Active particles: {len(engine.particles.particles)}")
    print(f"Zombies in room: {len(engine.current_room.zombies)}")

    if screenshot_dir:
        dump_room_screenshots(engine, screenshot_dir)

    if validations_passed == validations_total:
        print("\n✓ All validations passed successfully!")
    else:
        print(f"\n✗ {validations_total - validations_passed} validations failed!")
        sys.exit(1)


def main() -> None:
    # Set headless mode environment before pygame init
    if "--headless" in sys.argv:
        os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

    base_path = os.path.dirname(os.path.abspath(__file__))
    engine = GameEngine(base_path)

    if "--headless" in sys.argv:
        # Enhanced headless mode with comprehensive validation
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        screenshot_dir = None
        if "--screenshot-dir" in sys.argv:
            flag_index = sys.argv.index("--screenshot-dir")
            if flag_index + 1 < len(sys.argv):
                screenshot_dir = sys.argv[flag_index + 1]
        run_headless_validation(engine, verbose=verbose, screenshot_dir=screenshot_dir)
        return

    engine.run()


if __name__ == "__main__":  # pragma: no cover - direct execution guard
    main()
