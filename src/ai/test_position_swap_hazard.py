import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.ball_type = team
        self.is_flying = False

class MockHazard:
    def __init__(self, id, kind, x, y):
        self.id = id
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 20.0
        self.duration = 1.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.is_raining = False
        self.is_windy = False
        self.weather = "clear"
        self.width = 1000
        self.height = 1000
        self.clamp_position_called = False

    def clamp_position(self, x, y, r):
        self.clamp_position_called = True
        return x, y, False

class MockWorld:
    def __init__(self, balls, arena):
        self.balls = balls
        self.arena = arena
        self.tick = 100
        self.events = []
        self.items = []
        self.boosters = []

def test_position_swap_hazard_trigger():
    b1 = MockBall(id=1, team="TeamA", x=50.0, y=50.0)
    b2 = MockBall(id=2, team="TeamB", x=200.0, y=200.0)

    # Place hazard exactly at b1's location
    h = MockHazard(id=100, kind="position_swap_hazard", x=50.0, y=50.0)

    world = MockWorld(balls=[b1, b2], arena=MockArena(hazards=[h]))

    action = Action(b1, world)

    # Mock perception methods which _get_enemies might use internally if they are missing
    action._get_perception_radius = lambda: 1000.0

    # Ensure they start at correct positions
    assert b1.x == 50.0 and b1.y == 50.0
    assert b2.x == 200.0 and b2.y == 200.0

    # Execute action to trigger hazard loop
    # We will pass a zero delta to make sure velocity updates don't move the ball
    action.execute(strategy="idle", delta=0.0)

    # Also reset velocity to zero, just in case "idle" strategy gave it a random wander velocity
    # We just want to check if the teleport logic triggered successfully and swapped the coordinates
    # The actual x and y might be slightly offset by a bounce or physics update in the same tick
    # so we will check if the distance from the expected teleport target is small.

    # Hazard should be destroyed
    assert h.duration == 0.0

    # Positions should be swapped approximately
    import math
    dist1 = math.hypot(b1.x - 200.0, b1.y - 200.0)
    dist2 = math.hypot(b2.x - 50.0, b2.y - 50.0)

    assert dist1 < 50.0, f"b1 is too far from expected 200,200. b1 is at {b1.x},{b1.y}"
    assert dist2 < 50.0, f"b2 is too far from expected 50,50. b2 is at {b2.x},{b2.y}"

    # Teleport ticks should be updated
    assert getattr(b1, "last_teleport_tick") == 100
    assert getattr(b2, "last_teleport_tick") == 100

    # Teleport events should be generated
    teleport_events = [e for e in world.events if e["type"] == "teleport"]
    assert len(teleport_events) == 2
