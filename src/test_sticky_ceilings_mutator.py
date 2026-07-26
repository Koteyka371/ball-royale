import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class MockMode:
    def __init__(self, name="Reverse Gravity Event", active=True):
        self.name = name
        self.event_active = active

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = MockMode()
        self.gravity_reversal_active = False
        self.tick_timer = 0.0
        self.events = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, x, y, vx=500.0, vy=500.0, skill_timer=0.0):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.ball_type = "player"
        self.skill_timer = skill_timer

def test_sticky_ceilings_active():
    mutator = GAME_MODES["sticky_ceilings_mutator"]
    world = MockWorld()
    world.tick_timer = 2.0
    b1 = MockBall(400, 30) # near ceiling, not dashing

    mutator.setup(world, [b1])
    # Force sticky area directly on ball
    mutator.sticky_areas = [{"x": 400.0, "radius": 50.0}]

    mutator.tick(world, [b1], 0.1)

    # Speed is low enough (500^2 + 500^2 < 600,000) so it gets stuck and velocity reduced
    assert b1.vx == 50.0
    assert b1.vy == 50.0
    assert len(world.events) > 0
    assert world.events[0][0] == "visual_effect"

def test_sticky_ceilings_dashing():
    mutator = GAME_MODES["sticky_ceilings_mutator"]
    world = MockWorld()
    b1 = MockBall(400, 30, skill_timer=1.0) # dashing

    mutator.setup(world, [b1])
    mutator.sticky_areas = [{"x": 400.0, "radius": 50.0}]

    mutator.tick(world, [b1], 0.1)

    # Should not be slowed down because skill_timer > 0 (dashing)
    assert b1.vx == 500.0
    assert b1.vy == 500.0

def test_sticky_ceilings_fast():
    mutator = GAME_MODES["sticky_ceilings_mutator"]
    world = MockWorld()
    b1 = MockBall(400, 30, vx=1000.0, vy=1000.0) # 1,000^2 + 1,000^2 = 2,000,000 > 600,000

    mutator.setup(world, [b1])
    mutator.sticky_areas = [{"x": 400.0, "radius": 50.0}]

    mutator.tick(world, [b1], 0.1)

    # Should not be slowed down because velocity is too high
    assert b1.vx == 1000.0
    assert b1.vy == 1000.0

def test_sticky_ceilings_not_reverse_gravity():
    mutator = GAME_MODES["sticky_ceilings_mutator"]
    world = MockWorld()
    world.game_mode = MockMode(active=False) # Reverse gravity not active

    b1 = MockBall(400, 30)

    mutator.setup(world, [b1])
    mutator.sticky_areas = [{"x": 400.0, "radius": 50.0}]

    mutator.tick(world, [b1], 0.1)

    # Should not be slowed down because reverse gravity is off
    assert b1.vx == 500.0
    assert b1.vy == 500.0
