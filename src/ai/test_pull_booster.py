import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.speed = 0.0
        self.damage = 10.0
        self.base_damage = 10.0
        self._base_speed_set = True

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

def test_pull_booster_effect():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # Apply pull booster
    ball.pull_booster_timer = 5.0

    h1 = MockHazard("spikes", 600.0, 500.0, 15.0)
    world.arena.hazards.append(h1)

    h2 = MockHazard("trap", 400.0, 500.0, 20.0)
    world.arena.hazards.append(h2)

    h3 = MockHazard("stamina_booster", 500.0, 600.0, 50.0) # Should pull because of kind
    world.arena.hazards.append(h3)

    h4 = MockHazard("trap", 500.0, 400.0, 50.0) # Should NOT pull because radius >= 30 and not in pullable kinds
    world.arena.hazards.append(h4)

    action._update_skill_timer(0.1)

    # Check pull (150 * 0.1 = 15.0)
    assert h1.x == 585.0
    assert h2.x == 415.0
    assert h3.y == 585.0
    assert h4.y == 400.0 # Unchanged
