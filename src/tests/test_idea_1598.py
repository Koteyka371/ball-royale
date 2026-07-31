import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, cosmetic="", team=1):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.cosmetic = cosmetic
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.is_confused = False
        self.in_mirror_dimension = False
        self.speed_boost_timer = 0.0
        self.shield_timer = 0.0
        self.invulnerability_timer = 0.0
        self.damage_buff_timer = 0.0

    def get_hp_percent(self):
        return 1.0

class MockHazard:
    def __init__(self, x, y, kind, radius):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = 0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.time = 0.0
        self.events = []
        class Arena:
            def __init__(self):
                self.hazards = []
                self.weather = "normal"
                self.bounds = {"width": 1000, "height": 1000}
        self.arena = Arena()

    def get_nearby_entities(self, ball, radius):
        return {"allies": [b for b in self.balls if b.team == ball.team and b.id != ball.id], "enemies": [b for b in self.balls if b.team != ball.team]}

def test_link_boots_positive_effects():
    b1 = MockBall(1, 0, 0, "link_boots", 1)
    b2 = MockBall(2, 50, 0, "", 1)
    b3 = MockBall(3, 19, 0, "", 2)

    b1.speed_boost_timer = 5.0
    b2.shield_timer = 3.0

    world = MockWorld()
    world.balls = [b1, b2, b3]

    action = Action(b1, world)
    action._resolve_collisions()

    assert b1.speed_boost_timer == 5.0
    assert b2.speed_boost_timer == 5.0
    assert b1.shield_timer == 3.0
    assert b2.shield_timer == 3.0

def test_link_boots_hazard_repulsion():
    b1 = MockBall(1, 15, 0, "link_boots", 1)
    b2 = MockBall(2, 50, 0, "", 1)

    hazard = MockHazard(0, 0, "repulsion_zone", 20)

    world = MockWorld()
    world.balls = [b1, b2]
    world.arena.hazards = [hazard]

    action = Action(b1, world)
    action.execute("idle", 1.0)

    # Normally b1 gets pushed away by hazard.
    # With link_boots, the push is halved, and the nearest ally gets the other half.
    # Since b2 is an ally, it should move as well.
    assert b1.x > 15
    assert b2.x > 50
