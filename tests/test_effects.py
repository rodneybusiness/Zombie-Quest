"""Tests for visual effects system."""
import pytest
import pygame

# Initialize pygame for testing
pygame.init()


from zombie_quest.effects import (
    Particle,
    ParticleSystem,
    ScreenTransition,
    GlowEffect,
    ScreenShake,
)


class TestParticle:
    """Test particle behavior."""

    def test_particle_creation(self):
        p = Particle(
            x=100, y=100,
            vx=10, vy=-20,
            life=1.0, max_life=1.0,
            color=(255, 0, 0),
            size=5.0
        )
        assert p.x == 100
        assert p.y == 100
        assert p.life == 1.0

    def test_particle_update_moves(self):
        p = Particle(
            x=0, y=0,
            vx=100, vy=0,
            life=1.0, max_life=1.0,
            color=(255, 0, 0),
            size=5.0
        )
        result = p.update(0.5)  # 0.5 seconds
        assert result is True  # Still alive
        assert p.x == 50  # Moved 50 pixels (100 * 0.5)

    def test_particle_dies(self):
        p = Particle(
            x=0, y=0,
            vx=0, vy=0,
            life=0.1, max_life=1.0,
            color=(255, 0, 0),
            size=5.0
        )
        result = p.update(0.5)  # 0.5 seconds > 0.1 life
        assert result is False  # Dead

    def test_particle_gravity(self):
        p = Particle(
            x=0, y=0,
            vx=0, vy=0,
            life=1.0, max_life=1.0,
            color=(255, 0, 0),
            size=5.0,
            gravity=100
        )
        p.update(1.0)
        assert p.vy == 100  # Gravity applied


class TestParticleSystem:
    """Test particle system behavior."""

    def test_particle_system_creation(self):
        ps = ParticleSystem()
        assert len(ps.particles) == 0

    def test_emit_burst(self):
        ps = ParticleSystem()
        ps.emit_burst(100, 100, (255, 0, 0), count=10)
        assert len(ps.particles) == 10

    def test_update_removes_dead_particles(self):
        ps = ParticleSystem()
        ps.emit_burst(0, 0, (255, 0, 0), count=5, lifetime=0.1)
        assert len(ps.particles) == 5
        ps.update(1.0)  # All particles should die
        assert len(ps.particles) == 0


class TestScreenTransition:
    """Test screen transition behavior."""

    def test_transition_creation(self):
        st = ScreenTransition()
        assert st.active is False

    def test_start_transition(self):
        st = ScreenTransition()
        st.start_transition()
        assert st.active is True
        assert st.fade_in is False  # Starts by fading out

    def test_transition_complete_cycle(self):
        st = ScreenTransition()
        st.start_transition()

        # Update past fade out
        for _ in range(100):
            if not st.update(0.05):
                break

        assert st.active is False


class TestGlowEffect:
    """Test glow effect behavior."""

    def test_glow_creation(self):
        glow = GlowEffect()
        assert glow.time == 0.0

    def test_glow_update(self):
        glow = GlowEffect()
        glow.update(1.0)
        assert glow.time == 1.0

    def test_glow_intensity_range(self):
        glow = GlowEffect()
        for i in range(100):
            glow.update(0.1)
            intensity = glow.get_glow_intensity()
            assert 0.0 <= intensity <= 1.0


class TestScreenShake:
    """Test screen shake behavior."""

    def test_shake_creation(self):
        shake = ScreenShake()
        assert shake.intensity == 0.0

    def test_shake_activation(self):
        shake = ScreenShake()
        shake.shake(intensity=10.0, duration=0.5)
        assert shake.intensity == 10.0
        assert shake.duration == 0.5

    def test_shake_offset(self):
        shake = ScreenShake()
        shake.shake(intensity=10.0, duration=0.5)
        offset = shake.update(0.1)
        assert isinstance(offset, tuple)
        assert len(offset) == 2

    def test_shake_stops(self):
        shake = ScreenShake()
        shake.shake(intensity=10.0, duration=0.1)
        shake.update(0.2)  # Past duration
        offset = shake.update(0.0)
        assert offset == (0, 0)
