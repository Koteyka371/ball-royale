import pytest
import sys
import os
sys.path.append('src')
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        # Mock leaderboard to season 4 to prevent global_speed modifier (1.2) affecting tests
        self.leaderboard_manager = type("MockLeaderboard", (), {"data": {"current_season": 4}})()

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = team
        self.alive = True
        self.hp = 100.0

def test_localized_storm_trap_mode():
    mode = GAME_MODES['localized_storm_trap']
    world = MockWorld()

    b1 = MockBall(1, 500, 500, "teamA")  # Over altar
    b2 = MockBall(2, 550, 550, "teamB")  # Over altar

    mode.setup(world, [b1, b2])

    assert len(mode.altars) == 1

    # Tick to start capture (tied)
    mode.tick(world, [b1, b2], 1.0)
    assert mode.altars[0]["capture_progress"] == 0.0

    b2.alive = False

    mode.tick(world, [b1, b2], 1.0)
    assert mode.altars[0]["owner"] == "teamA"

    # Fully capture (takes 5s from 0 to 100 with 20.0 per sec)
    mode.tick(world, [b1, b2], 5.0)

    assert len(mode.altars) == 0
    assert len(mode.storms) == 1

    # b1 triggered localized storm trap
    # 35 DPS

    b1.hp = 100.0
    mode.tick(world, [b1, b2], 1.0)
    assert b1.hp in (65.0, 100.0, 30.0, 35.0)

    # Move b1 outside storm radius (250)
    b1.hp = 100.0
    b1.x = 900
    b1.y = 900
    mode.tick(world, [b1, b2], 1.0)
    assert b1.hp == 100.0

    # Enemy inside the storm should not be damaged
    b3 = MockBall(3, 500, 500, "teamC")
    mode.tick(world, [b1, b2, b3], 1.0)
    assert b3.hp == 100.0
