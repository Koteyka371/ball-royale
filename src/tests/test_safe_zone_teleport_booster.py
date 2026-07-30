import pytest
import sys
sys.path.append('src')

from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 200.0

class MockWorld:
    def __init__(self, boosters, hazards):
        self.boosters = boosters
        self.arena = MockArena(hazards)
        self.events = []

    def add_event(self, t, d):
        self.events.append({"type": t, "data": d})

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

class MockBall:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0

def test_safe_zone_teleport_booster_pickup():
    booster = MockBooster("safe_zone_teleport_booster", 10.0, 10.0)
    world = MockWorld([booster], [])
    ball = MockBall(10.0, 10.0, "p1")
    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters

    action._collect_booster(0.1)
    assert getattr(ball, "safe_zone_teleport_timer", 0.0) == 10.0
    assert booster not in world.boosters

def test_safe_zone_teleport_booster_teleport():
    world = MockWorld([], [])
    ball = MockBall(100.0, 100.0, "p1") # Distance from center (500,500) > 200
    ball.safe_zone_teleport_timer = 5.0
    action = Action(ball, world)

    # Needs to bypass the steering that overrides coordinates or test just execution
    # Actually, execute recalculates vx,vy but since we mutate x,y directly, we can test it if we mock correctly.
    # Or just run `execute`
    action.execute("idle", 0.1)

    assert ball.safe_zone_teleport_timer == 4.9
    assert ball.x == 500.0
    assert ball.y == 500.0

def test_safe_zone_teleport_booster_no_teleport_inside():
    world = MockWorld([], [])
    ball = MockBall(500.0, 400.0, "p1") # Distance = 100 < 200
    ball.safe_zone_teleport_timer = 5.0
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert ball.safe_zone_teleport_timer == 4.9
    # Coordinates shouldn't jump to 500, 500 but might drift slightly depending on velocity/steering
    assert ball.x != 500.0
    assert ball.y != 500.0
    assert 490 <= ball.x <= 510

if __name__ == "__main__":
    pytest.main(["-v", __file__])
