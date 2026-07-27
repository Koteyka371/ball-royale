import pytest
from src.ai.game_modes import MercenaryOutpostMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.tick_timer = 0.0
        self.arena = MockArena()
        self.balls = []
        self.next_id = 1000

    def add_event(self, event_type, data):
        pass

class MockBall:
    def __init__(self, ball_id, x, y, team):
        self.id = ball_id
        self.x = x
        self.y = y
        self.radius = 20.0
        self.team = team
        self.ball_type = team
        self.alive = True

def test_mercenary_outpost_mode():
    mode = MercenaryOutpostMode()
    world = MockWorld()

    # Setup
    mode.setup(world, [])
    assert len(mode.outposts) == 2, "Should spawn 2 outposts"

    outpost = mode.outposts[0]
    outpost["x"] = 500
    outpost["y"] = 500
    outpost["capture_progress"] = 0.0
    outpost["owner"] = None

    # Create a ball to capture the outpost
    b1 = MockBall(1, 500, 500, "team1")
    world.balls.append(b1)

    # Apply traits to capture the outpost (needs 5 seconds at 20.0 per sec)
    delta = 1.0
    for _ in range(6):
        mode.apply_dynamic_traits(world, [b1], delta)

    assert outpost["owner"] == "team1", "Outpost should be owned by team1"

    # Spawn timer should now tick down (starts at 5.0)
    for _ in range(6):
        mode.apply_dynamic_traits(world, [b1], delta)

    # Should have spawned a minion
    assert len(world.balls) > 1, "Minion should have been spawned"

    minions = [b for b in world.balls if getattr(b, "ball_type", "") == "minion"]
    assert len(minions) > 0, "Minion ball type should exist"
    assert minions[0].team == "team1", "Minion should belong to capturing team"
