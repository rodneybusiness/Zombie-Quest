"""Tests for character system."""
import pytest
import pygame

# Initialize pygame for testing
pygame.init()


from zombie_quest.characters import Hero, Zombie, ZombieSpawner, Character, AnimationState


class TestAnimationState:
    """Test animation state tracking."""

    def test_default_state(self):
        state = AnimationState()
        assert state.direction == "down"
        assert state.frame_index == 0
        assert state.frame_time == 0.0


class TestHero:
    """Test hero character functionality."""

    def test_hero_creation(self):
        hero = Hero((100, 100))
        assert hero.position.x == 100
        assert hero.position.y == 100

    def test_hero_health(self):
        hero = Hero((0, 0))
        assert hero.health == hero.max_health
        assert hero.is_dead() is False

    def test_hero_take_damage(self):
        hero = Hero((0, 0))
        initial_health = hero.health
        hero.take_damage(1)
        assert hero.health == initial_health - 1
        assert hero.is_invincible is True

    def test_hero_invincibility_blocks_damage(self):
        hero = Hero((0, 0))
        hero.take_damage(1)
        initial_health = hero.health
        hero.take_damage(1)  # Should be blocked
        assert hero.health == initial_health

    def test_hero_death(self):
        hero = Hero((0, 0))
        for _ in range(10):  # Ensure we can kill
            hero.is_invincible = False
            hero.take_damage(1)
            if hero.is_dead():
                break
        assert hero.is_dead() is True

    def test_hero_heal(self):
        hero = Hero((0, 0))
        hero.is_invincible = False
        hero.take_damage(1)
        damaged_health = hero.health
        hero.heal(1)
        assert hero.health == damaged_health + 1

    def test_hero_heal_cap(self):
        hero = Hero((0, 0))
        hero.heal(100)  # Try to overheal
        assert hero.health == hero.max_health

    def test_hero_keyboard_movement(self):
        hero = Hero((100, 100))
        # Simulate keyboard press
        hero.using_keyboard = True
        hero.keyboard_velocity = pygame.Vector2(1, 0)
        hero.update(0.1)
        # Should have moved right
        assert hero.position.x > 100


class TestZombie:
    """Test zombie character functionality."""

    def test_zombie_creation(self):
        zombie = Zombie((100, 100))
        assert zombie.position.x == 100
        assert zombie.position.y == 100

    def test_zombie_types(self):
        for ztype in ["scene", "bouncer", "rocker", "dj"]:
            zombie = Zombie((0, 0), zombie_type=ztype)
            assert zombie.zombie_type == ztype

    def test_zombie_groan_timer(self):
        zombie = Zombie((0, 0))
        # Fast forward timer
        zombie.groan_timer = 0.0
        assert zombie.should_groan() is True
        assert zombie.groan_timer > 0  # Reset


class TestZombieSpawner:
    """Test zombie spawning functionality."""

    def test_create_zombie(self):
        zombie = ZombieSpawner.create_zombie((100, 100))
        assert isinstance(zombie, Zombie)
        assert zombie.position.x == 100

    def test_create_zombie_for_room(self):
        zombie = ZombieSpawner.create_zombie((0, 0), "record_store")
        assert zombie.zombie_type in ["scene", "rocker"]

    def test_create_zombies_from_data(self):
        data = [
            {"position": [100, 100]},
            {"position": [200, 200], "type": "bouncer"},
        ]
        zombies = ZombieSpawner.create_zombies_for_room(data)
        assert len(zombies) == 2
        assert zombies[1].zombie_type == "bouncer"
