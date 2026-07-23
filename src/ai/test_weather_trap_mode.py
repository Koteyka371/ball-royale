import pytest
import sys
import os
sys.path.append('src')
from ai.game_modes import WeatherTrapMode

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
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.hp = 100.0
        self.base_perception_radius = 200.0
        self.perception_radius = 200.0

def test_weather_trap_mode():
    mode = WeatherTrapMode()
    world = MockWorld()

    b1 = MockBall(1, 250, 250, "teamA")  # Over altar 0 (sandstorm)
    b2 = MockBall(2, 750, 750, "teamB")  # Over altar 1 (blizzard)

    mode.setup(world, [b1, b2])

    assert len(mode.altars) == 4

    # Tick to start capture
    mode.tick(world, [b1, b2], 1.0)
    assert mode.altars[0]["capture_progress"] == 0.0
    assert mode.altars[0]["owner"] == "teamA"

    assert mode.altars[1]["capture_progress"] == 0.0
    assert mode.altars[1]["owner"] == "teamB"

    # Fully capture (takes 5s from 0 to 100 with 20.0 per sec)
    mode.tick(world, [b1, b2], 1.0)
    assert mode.altars[0]["capture_progress"] == 20.0
    mode.tick(world, [b1, b2], 4.0)

    assert len(mode.altars) == 2
    assert len(mode.active_traps) == 2

    # b1 triggered sandstorm trap
    # Sandstorm: speed 0.7, dot 2.0 * delta
    assert b1.speed == 70.0
    b1.hp = 100.0
    mode.tick(world, [b1, b2], 1.0)
    assert b1.hp == 98.0
    assert b1.speed == 70.0

    # b2 triggered blizzard trap
    # Blizzard: speed 0.5
    assert b2.speed == 50.0
    assert b2.hp == 100.0  # no dot

    # Check that another team is not affected
    b3 = MockBall(3, 500, 500, "teamC")
    mode.tick(world, [b1, b2, b3], 1.0)
    assert b3.speed == 100.0
    assert b3.damage == 10.0
