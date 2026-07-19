import pytest
import random
from ai.game_modes import SolarEclipseEventMode

class MockHazard:
    def __init__(self):
        self.kind = "solar_panel"
        self.efficiency = 1.0

class MockArena:
    def __init__(self):
        self.is_night = False
        self.is_solar_eclipse = False
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = [MockHazard()]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "player"
        self.vision_radius = 500.0
        self.invisible = False

def test_solar_eclipse_mode_mechanics():
    mode = SolarEclipseEventMode()
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls)

    original_random = random.random
    try:
        # Fast forward timer to > 30 and force trigger
        mode.event_timer = 35.0
        random.random = lambda: 0.1

        # Trigger event (event_duration = 30.0)
        mode.tick(world, balls, delta=0.1)
        assert mode.event_active is True
        assert world.arena.is_solar_eclipse is True
        assert world.arena.is_night is True

        # Progress starts at 1.0. Move to full totality (event_duration = 15.0)
        # We need to drop 15 seconds.
        mode.tick(world, balls, delta=15.0)

        # At totality (duration = 15.0), progress should be 0.0
        assert balls[0].vision_radius == 50.0
        assert balls[0].invisible is True
        assert world.arena.hazards[0].efficiency < 0.1

        # Monsters should spawn since duration is 15.0 (between 10.0 and 20.0)
        monsters = getattr(mode, "eclipse_monsters", [])
        assert len(monsters) > 0
        assert monsters[0].ball_type == "shadow_monster"

        # Move past totality (event_duration = 5.0)
        mode.tick(world, balls, delta=10.0)
        assert balls[0].invisible is False
        assert balls[0].vision_radius > 50.0
        assert world.arena.hazards[0].efficiency > 0.0

        # End event (event_duration = 0.0)
        mode.tick(world, balls, delta=6.0)
        assert mode.event_active is False
        assert world.arena.is_solar_eclipse is False
        assert balls[0].invisible is False
        assert balls[0].vision_radius == 500.0
        assert world.arena.hazards[0].efficiency == 1.0

        # Monsters should be dead and cleared
        monsters = getattr(mode, "eclipse_monsters", [])
        assert len(monsters) == 0

    finally:
        random.random = original_random
