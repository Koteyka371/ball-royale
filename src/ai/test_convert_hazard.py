import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.damage = 10.0
        self.duration = 0.0
        self.owner_id = None

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []

class MockBall:
    def __init__(self, x, y, skill):
        self.x = x
        self.y = y
        self.skill = skill
        self.id = 1
        self.skill_timer = 0.0
        self.skill_cooldown = 10.0
        self.silence_timer = 0.0

def test_convert_hazard_skill():
    h1 = MockHazard(10, 10, "spikes")
    h2 = MockHazard(1000, 1000, "spikes") # Too far
    arena = MockArena([h1, h2])
    world = MockWorld(arena)
    ball = MockBall(0, 0, "convert_hazard")
    action = Action(ball, world)

    assert h1.kind == "spikes"
    assert h1.damage == 10.0

    action._use_skill()

    assert h1.kind in ["event_horizon_trap", "healing_spring", "booster", "defensive_shield"]
    assert h1.damage == 0.0
    assert h1.duration == 10.0
    assert h1.owner_id == 1
    assert ball.skill_timer == 10.0

    assert h2.kind == "spikes" # Untouched
