import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.leaderboard_manager = type("Mock", (), {"data": {"current_season": 0}})()

class MockBall:
    def __init__(self, team, x, y):
        self.ball_type = team
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.speed = 100.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_weather_stations_capture():
    mode = GAME_MODES["weather_stations"]
    world = MockWorld()

    # Place a ball directly on the first station
    # Station 0 is at 250, 250
    b1 = MockBall("teamA", 250, 250)
    mode.setup(world, [b1])

    delta = 0.1
    # Tick enough to capture (progress increases by 20 * delta per tick)
    for _ in range(60):
        mode.tick(world, [b1], delta)

    # Station 0 should now be captured by teamA and its weather is "heatwave"
    assert mode.stations[0]["capture_progress"] == 100.0
    assert mode.stations[0]["owner"] == "teamA"

def test_weather_stations_effects():
    mode = GAME_MODES["weather_stations"]
    world = MockWorld()

    # Station 0 is at 250, 250 (heatwave)
    # Station 1 is at 750, 250 (blizzard)
    b1 = MockBall("teamA", 250, 250)
    b2 = MockBall("teamB", 750, 250)

    mode.setup(world, [b1, b2])

    # Capture both stations
    mode.stations[0]["capture_progress"] = 100.0
    mode.stations[0]["owner"] = "teamA"

    mode.stations[1]["capture_progress"] = 100.0
    mode.stations[1]["owner"] = "teamB"

    mode.tick(world, [b1, b2], 0.1)

    # For station 0 (heatwave), teamA should be buffed
    # assert abs(b1.speed - 120.0) < 0.01
    assert abs(b1.speed - (b1.base_speed * 1.2)) < 0.01
    # assert abs(b1.damage - 15.0) < 0.01
    assert abs(b1.damage - (b1.base_damage * 1.5)) < 0.01

    # For station 1 (blizzard), teamB should be buffed
    # assert abs(b2.speed - 150.0) < 0.01
    assert abs(b2.speed - (b2.base_speed * 1.5)) < 0.01
    # assert abs(b2.damage - 12.0) < 0.01
    assert abs(b2.damage - (b2.base_damage * 1.2)) < 0.01

    # Now move b2 into station 0's sector
    b2.x = 250
    b2.y = 250
    mode.tick(world, [b1, b2], 0.1)

    # b2 is not teamA, so in heatwave it gets debuffed
    # assert abs(b2.speed - 80.0) < 0.01
    assert abs(b2.speed - (b2.base_speed * 0.8)) < 0.01
    # assert abs(b2.damage - 10.0) < 0.01
    assert abs(b2.damage - (b2.base_damage * 1.0)) < 0.01
