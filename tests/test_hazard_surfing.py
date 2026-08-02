import pytest
from ai.action import Action
from typing import Any, List

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls: List[Any] = []
        self.arena = MockArena()
        self.tick = 0
        self.time = 0.0

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.team = 1
        self.ball_type = "base"
        self.alive = True
        self.skill = "hazard_surfing"
        self.skill_timer = 0.0
        self.active_skills = []

class MockHazard:
    def __init__(self, x, y, kind, radius):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = 10.0
        self.duration = 10.0

def test_hazard_surfing():
    world = MockWorld()
    ball = MockBall(0.0, 0.0)
    world.balls.append(ball)

    lava_hazard = MockHazard(0.0, 0.0, "lava", 100.0)
    world.arena.hazards.append(lava_hazard)

    action = Action(ball, world)

    # Check surfing activation
    action.execute("idle", 0.05)

    # It should become immune to hazards
    assert ball.hazard_immunity_timer > 0.0
    # It should gain a speed boost
    assert ball.speed_multiplier > 1.0
    # It should leave a fire trail
    assert len(world.arena.hazards) > 1
    assert world.arena.hazards[-1].kind == "fire"

if __name__ == "__main__":
    test_hazard_surfing()

    # Test end of surfing
    ball.surfing_timer = 0.05
    ball.was_surfing = True
    action.execute("idle", 0.1)

    # Speed multiplier should reset
    assert ball.speed_multiplier == 1.0
