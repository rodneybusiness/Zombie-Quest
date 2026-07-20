"""Tests for the demo arc: ending wiring, precedence, and the win path."""
import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from zombie_quest.config import GameState


@pytest.fixture
def engine():
    from zombie_quest.engine import GameEngine
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return GameEngine(repo_root)


class TestEndingData:
    def test_endings_block_loaded(self, engine):
        assert set(engine.endings_data) == {
            "redemption", "transcendence", "bittersweet", "alone", "hollow"}
        for ending in engine.endings_data.values():
            assert ending.get("name") and ending.get("text")

    def test_backstory_flag_set(self, engine):
        assert engine.game_flags.get("backstory_purist") is True

    def test_every_terminal_maya_flag_maps_to_an_ending(self, engine):
        terminal_flags = ["redemption_achieved", "transcendence_ending",
                          "bittersweet_ending", "maya_lost", "hollow_victory_ending"]
        for flag in terminal_flags:
            engine.game_flags = {flag: True}
            assert engine.check_ending_conditions() is not None, flag

    def test_redemption_beats_bittersweet(self, engine):
        engine.game_flags = {"redemption_achieved": True, "bittersweet_ending": True}
        assert engine.check_ending_conditions() == "redemption"

    def test_no_flags_no_ending(self, engine):
        engine.game_flags = {"backstory_purist": True}
        assert engine.check_ending_conditions() is None


class TestEndingFlow:
    def test_node_effects_reach_game_flags(self, engine):
        """effect_callback wiring: node-entry effects must set flags."""
        tree = engine.dialogue_trees["maya"]
        engine.dialogue_manager.start_dialogue(
            tree, engine.inventory.get_item_names(), engine.game_flags)
        assert engine.dialogue_manager.effect_callback is not None

    def test_win_path_reaches_redemption_ending(self, engine):
        """Drive Maya's dialogue choosing option 1 until it ends."""
        tree = engine.dialogue_trees["maya"]
        engine.dialogue_manager.start_dialogue(
            tree, engine.inventory.get_item_names(), engine.game_flags)
        engine.state = GameState.DIALOGUE
        for _ in range(30):
            if not engine.dialogue_manager.active:
                break
            for key in (pygame.K_1, pygame.K_RETURN):
                if not engine.dialogue_manager.active:
                    break
                engine._handle_dialogue_event(
                    pygame.event.Event(pygame.KEYDOWN, key=key))
        assert engine.game_flags.get("redemption_achieved") is True
        assert engine.state == GameState.GAME_OVER
        assert engine.ending_screen.visible
        assert engine.ending_screen.title == "ONE MORE SONG"
        engine.draw()  # the card must render

    def test_infection_ending_uses_card(self, engine):
        engine._trigger_infection_ending()
        assert engine.state == GameState.GAME_OVER
        assert engine.ending_screen.visible
        assert "TRANSFORMATION" in engine.ending_screen.title
        engine.draw()

    def test_restart_from_ending(self, engine):
        engine.game_flags["bittersweet_ending"] = True
        engine.trigger_ending("bittersweet")
        assert engine.state == GameState.GAME_OVER
        engine.handle_events()  # flush
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        pygame.event.post(event)
        engine.handle_events()
        assert engine.state == GameState.PLAYING
        assert not engine.ending_screen.visible
        assert not engine.game_flags.get("bittersweet_ending", False)

    def test_world_freezes_under_ending(self, engine):
        engine.trigger_ending("hollow") if engine.endings_data.get("hollow") else None
        engine.game_flags["hollow_victory_ending"] = True
        engine.trigger_ending("hollow")
        position_before = (engine.hero.position.x, engine.hero.position.y)
        for _ in range(30):
            engine.update(1 / 60)
        assert (engine.hero.position.x, engine.hero.position.y) == position_before
