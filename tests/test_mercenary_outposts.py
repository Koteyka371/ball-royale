import pytest
from ai.mercenary_outposts import MercenaryOutpostsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x, y, team, is_mercenary=False):
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = "normal"
        self.is_mercenary = is_mercenary
        self.id = 1

def test_mercenary_outposts_setup():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    mode.setup(world, [])
    assert len(mode.outposts) == 4
    assert mode.outposts[0]["radius"] == 100.0

def test_mercenary_outposts_capture():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    mode.setup(world, [])

    # Place a ball from Team 1 exactly on the first outpost
    outpost = mode.outposts[0]
    ball = MockBall(outpost["x"], outpost["y"], "Team1")
    world.balls.append(ball)

    # Simulate time to fully capture the outpost (20 progress per sec -> 5 secs)
    for _ in range(60): # 6 seconds at 0.1 delta
        mode.apply_dynamic_traits(world, world.balls, 0.1)

    assert outpost["owner"] == "Team1"
    assert outpost["capture_progress"] == 100.0

def test_mercenary_outposts_spawn_mercenary():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    mode.setup(world, [])

    outpost = mode.outposts[0]
    outpost["owner"] = "Team1"
    outpost["capture_progress"] = 100.0

    # Simulate time to trigger mercenary spawn (spawn every 10 secs)
    for _ in range(110): # 11 seconds at 0.1 delta
        mode.apply_dynamic_traits(world, world.balls, 0.1)

    # Check if a mercenary spawned
    mercenaries = [b for b in world.balls if getattr(b, "is_mercenary", False)]
    assert len(mercenaries) >= 1
    assert mercenaries[0].team == "Team1"

def test_mercenary_outposts_contested():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    mode.setup(world, [])

    outpost = mode.outposts[0]

    ball1 = MockBall(outpost["x"], outpost["y"], "Team1")
    ball2 = MockBall(outpost["x"], outpost["y"], "Team2")
    world.balls.extend([ball1, ball2])

    for _ in range(20):
        mode.apply_dynamic_traits(world, world.balls, 0.1)

    # Should not capture at all
    assert outpost["owner"] is None
    assert outpost["capture_progress"] == 0.0
