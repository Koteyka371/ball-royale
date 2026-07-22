import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 0.0
        self.active = True
        self.duration = 100.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.next_id = 999
        self.events = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.speed = 100.0
        self.team = 1
        self.alive = True
        self.invert_timer = 0.0
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0

def test_confusion_zone_effect():
    world = MockWorld()

    hazard = MockHazard(id=1, x=100.0, y=100.0, radius=50.0, kind="confusion_zone")
    world.arena.hazards.append(hazard)

    ball = MockBall(id=1, x=100.0, y=100.0)
    action = Action(ball, world)

    # Stay in the zone for a bit more than 3 seconds total
    action.execute("idle", 2.0)
    assert getattr(ball, "confusion_zone_timer", 0.0) == 2.0
    assert ball.invert_timer == 0.0

    action.execute("idle", 2.0)
    assert ball.confusion_zone_timer == 4.0
    assert ball.invert_timer > 0.0

    # Move out of the zone
    ball.x = 200.0
    ball.y = 200.0

    action.execute("idle", 0.1)
    assert ball.confusion_zone_timer == 0.0
