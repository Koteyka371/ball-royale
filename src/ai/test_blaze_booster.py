import pytest
import math
from ai.action import Action
from arena.procedural_arena import Hazard

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
        self.speed = 20.0
        self.damage = 10.0
        self.base_damage = 10.0
        self._base_speed_set = True

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

def test_blaze_booster_effect():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    ball.blaze_booster_timer = 5.0

    action._update_skill_timer(0.1)

    assert ball.blaze_booster_timer < 5.0

    # Speed is > 10, should drop a fire zone, but it's random (20% chance). Let's simulate enough ticks to drop fire.
    found_fire = False
    for _ in range(100):
        action._update_skill_timer(0.1)
        if any(h.kind == "fire_zone" for h in world.arena.hazards):
            found_fire = True
            break

    assert found_fire
