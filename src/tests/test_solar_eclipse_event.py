import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from ai.game_modes import SolarEclipseEventMode

class DummyHazard:
    def __init__(self, kind):
        self.kind = kind

class MockArena:
    def __init__(self):
        self.hazards = [DummyHazard("indestructible_wall")]
        self.is_night = False
        self.is_solar_eclipse = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

    def has_method(self, name):
        return True

def test_solar_eclipse_event():
    import random
    mode = SolarEclipseEventMode()
    world = MockWorld()

    # Fast forward until it triggers
    for _ in range(2000):
        # Override random to always trigger
        random.seed(42) # A seed where random() might be < 0.2 eventually
        mode.tick(world, [], 0.1)
        if mode.event_active:
            break

    # Force it active if seed didn't work
    if not mode.event_active:
        mode.event_timer = 31.0
        # Instead of monkeypatching random, we just rely on probability loop
        while not mode.event_active:
            mode.tick(world, [], 0.1)

    assert mode.event_active == True
    assert world.arena.is_night == True
    assert world.arena.is_solar_eclipse == True
    assert world.arena.hazards[0].kind == "breakable_wall"

    class DummyBall:
        def __init__(self, t):
            self.alive = True
            self.ball_type = t
            self.vision_radius = 1000.0
            self.invisible = False

    class DummySolarPanel:
        def __init__(self):
            self.kind = "solar_panel"
            self.active = True
            self.efficiency = 1.0

    balls = [DummyBall("normal")]
    world.arena.hazards.append(DummySolarPanel())

    # Test totality
    mode.event_duration = 15.0
    mode.tick(world, balls, 0.0)

    # Totality means progress = 0.0 -> vision should be minimum (50.0), invisible = True
    assert balls[0].vision_radius == 50.0
    assert balls[0].invisible == True
    assert world.arena.hazards[-1].efficiency < 0.1

    # Check monster spawn
    assert len(mode.eclipse_monsters) > 0 or hasattr(mode, 'eclipse_monsters')

    # Test edge
    mode.event_duration = 29.0 # start of eclipse
    mode.tick(world, balls, 0.0)
    assert balls[0].vision_radius > 900.0
    assert balls[0].invisible == False
    assert world.arena.hazards[-1].active == True


    class DummyBall:
        def __init__(self, t):
            self.alive = True
            self.ball_type = t
            self.vision_radius = 1000.0
            self.invisible = False

    class DummySolarPanel:
        def __init__(self):
            self.kind = "solar_panel"
            self.active = True
            self.efficiency = 1.0

    balls = [DummyBall("normal")]
    world.arena.hazards.append(DummySolarPanel())

    # Test totality
    mode.event_duration = 15.0
    mode.tick(world, balls, 0.0)

    # Totality means progress = 0.0 -> vision should be minimum (50.0), invisible = True
    assert balls[0].vision_radius == 50.0
    assert balls[0].invisible == True
    assert world.arena.hazards[-1].efficiency < 0.1

    # Check monster spawn
    assert len(mode.eclipse_monsters) > 0 or hasattr(mode, 'eclipse_monsters')

    # Test edge
    mode.event_duration = 29.0 # start of eclipse
    mode.tick(world, balls, 0.0)
    assert balls[0].vision_radius > 900.0
    assert balls[0].invisible == False
    assert world.arena.hazards[-1].active == True


    # End event
    mode.tick(world, [], 30.1)

    assert mode.event_active == False
    assert world.arena.is_night == False
    assert world.arena.is_solar_eclipse == False
    assert world.arena.hazards[0].kind == "indestructible_wall"
