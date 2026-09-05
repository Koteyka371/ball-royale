import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, is_turret=False):
        self.alive = True
        self.slow_timer = 0.0
        self.is_turret = is_turret
        self.hp = 100
        self.energy_shield_active = True
        self.surge_shield_active = True

class MockHazard:
    def __init__(self, kind):
        self.kind = kind

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()

def test_global_emp_event():
    mode = GAME_MODES["global_emp_event"]
    world = MockWorld()

    b1 = MockBall(is_turret=False)
    b2 = MockBall(is_turret=True)
    balls = [b1, b2]

    h1 = MockHazard("some_trap")
    h2 = MockHazard("deployable_stasis_bubble")
    h3 = MockHazard("turret_hazard")
    world.arena.hazards = [h1, h2, h3]

    mode.emp_timer = 0.01
    mode.tick(world, balls, 0.016)

    # Assert timer reset
    assert mode.emp_timer > 0
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'global_emp_pulse'

    # Assert slow applied
    assert b1.slow_timer >= 3.0

    # Assert turret died
    assert not b2.alive
    assert b2.hp == 0

    # Assert shields cleared
    assert not getattr(b1, "energy_shield_active", True)
    assert not getattr(b1, "surge_shield_active", True)

    # Assert deployables and turrets and shields removed
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "some_trap"
