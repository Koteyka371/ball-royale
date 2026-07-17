import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, alive=True):
        self.alive = alive
        self.is_frictionless = False
        self.frictionless_modifier_applied = False

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_frictionless_arena_modifier_registered():
    assert "frictionless_arena_modifier" in GAME_MODES
    mode = GAME_MODES["frictionless_arena_modifier"]
    assert mode.name == "Frictionless Arena Modifier"
    assert mode.is_active == False

def test_frictionless_arena_modifier_activation_and_deactivation():
    mode = GAME_MODES["frictionless_arena_modifier"]
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    # Fast forward event timer
    mode.event_timer = 0.1
    mode.tick(world, balls, 0.2)

    assert mode.is_active == True
    assert len(world.events) == 1
    assert world.events[0][0] == "frictionless_arena_start"

    for b in balls:
        assert b.is_frictionless == True
        assert b.frictionless_modifier_applied == True

    # Fast forward duration timer
    mode.duration_timer = 0.1
    mode.tick(world, balls, 0.2)

    assert mode.is_active == False
    for b in balls:
        assert b.is_frictionless == False
        assert b.frictionless_modifier_applied == False
