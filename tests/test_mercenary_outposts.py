import pytest
from ai.mercenary_outposts import MercenaryOutpostsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.tick_timer = 0.0
        self.arena = MockArena()
        self.balls = []
        self.entities = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.ball_type = team
        self.x = x
        self.y = y
        self.alive = True

def test_mercenary_outpost_capture():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    # Check outposts were created
    assert len(mode.outposts) == 3
    assert len(world.arena.hazards) == 3

    outpost = mode.outposts[0]
    outpost["x"] = 500
    outpost["y"] = 500

    ball = MockBall("b1", "team_a", 500, 500)
    balls.append(ball)

    # Tick to start capture
    mode.tick(world, balls, delta=1.0)
    assert outpost["capturing_team"] == "team_a"
    assert outpost["capture_progress"] > 0.0

    # Tick to complete capture
    mode.tick(world, balls, delta=10.0)
    assert outpost["controlling_team"] == "team_a"
    assert outpost["capture_progress"] == 100.0

    # Tick to trigger spawn (should spawn immediately on capture based on logic)
    mode.tick(world, balls, delta=0.1)

    mercs = [b for b in balls if getattr(b, "ball_type", "") == "mercenary"]
    assert len(mercs) > 0
    assert mercs[0].team == "team_a"

def test_mercenary_outpost_enemy_steal():
    mode = MercenaryOutpostsMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)
    outpost = mode.outposts[0]
    outpost["x"] = 500
    outpost["y"] = 500

    ball = MockBall("b1", "team_a", 500, 500)
    balls.append(ball)

    mode.tick(world, balls, delta=1.0)
    assert outpost["capturing_team"] == "team_a"

    mode.tick(world, balls, delta=10.0)
    assert outpost["controlling_team"] == "team_a"
    assert outpost["capture_progress"] == 100.0

    # Team B arrives
    ball2 = MockBall("b2", "team_b", 500, 500)
    balls.remove(ball)
    balls.append(ball2)

    # Should start reducing A's progress, not instantly capping
    mode.tick(world, balls, delta=1.0)
    assert outpost["capture_progress"] < 100.0
    assert outpost["controlling_team"] == "team_a" # still controlled until fully lost/captured

    # Tick heavily to fully lose A and start capturing for B
    mode.tick(world, balls, delta=20.0)
    assert outpost["capturing_team"] == "team_b"
    assert outpost["capture_progress"] == 100.0
    assert outpost["controlling_team"] == "team_b"
