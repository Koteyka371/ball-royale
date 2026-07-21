import pytest
from ai.game_modes import TimeRewindAltarMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, bid, team, x, y, hp, alive):
        self.id = bid
        self.team = team
        self.ball_type = team
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive

def test_time_rewind_altar_mode():
    mode = TimeRewindAltarMode()
    world = MockWorld()

    b1 = MockBall(1, "teamA", 100.0, 100.0, 100.0, True)
    b2 = MockBall(2, "teamB", 900.0, 900.0, 100.0, True)
    balls = [b1, b2]

    mode.setup(world, balls)

    b1.x = 500.0
    b1.y = 500.0

    # tick 1 (t=1.0)
    mode.tick(world, balls, 1.0)

    b2.x = 800.0
    # tick 2 (t=2.0)
    mode.tick(world, balls, 1.0)

    b2.x = 700.0
    # tick 3 (t=3.0)
    mode.tick(world, balls, 1.0)

    b2.x = 600.0
    # tick 4 (t=4.0)
    mode.tick(world, balls, 1.0)

    b2.x = 500.0
    # tick 5 (t=5.0)
    mode.tick(world, balls, 1.0)

    b2.x = 400.0
    # tick 6 (t=6.0) - capture completes here (1 tick claim + 5 ticks 20.0 = 100.0)
    mode.tick(world, balls, 1.0)

    # At t=6.0, history contains t=1.0, 2.0, 3.0, 4.0, 5.0, 6.0
    # But wait, history prune removes > 5.0. 6.0 - 5.0 = 1.0, so t=1.0 is still valid!
    # Wait, the oldest state before t=6.0 was recorded at t=1.0. At t=1.0, b2 was at 900.0.

    assert mode.altar["capture_progress"] == 0.0
    assert mode.altar["cooldown"] > 0

    assert b2.x == 900.0
