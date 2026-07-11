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
        # Prevent global season modifier from changing speed/damage (index 4 is cooldown)
        self.leaderboard_manager = type("Mock", (), {"data": {"current_season": 0}})()

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

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

def test_weather_clash_altar_capture():
    mode = GAME_MODES["weather_clash"]
    world = MockWorld()

    b1 = MockBall("teamA", 250, 500)
    mode.setup(world, [b1])


    delta = 0.1
    for _ in range(60):
        mode.tick(world, [b1], delta)
        print(f"owner: {mode.altars[0]['owner']}, progress: {mode.altars[0]['capture_progress']}")

    assert mode.weather == "heatwave"


def test_weather_clash_weather_effects():
    mode = GAME_MODES["weather_clash"]
    world = MockWorld()

    b1 = MockBall("teamA", 0, 0)
    mode.setup(world, [b1])

    # capture what it is after setup
    base_speed = b1.base_speed
    base_damage = b1.base_damage

    # Give b1 the winning team status
    mode.winning_team = "teamA"

    # Test heatwave for winner
    mode.weather = "heatwave"
    mode.tick(world, [b1], 0.1)

    # Due to floating point math
    assert abs(b1.speed - (base_speed * 1.2)) < 0.01
    assert abs(b1.damage - (base_damage * 1.5)) < 0.01

    # Test blizzard for winner
    mode.weather = "blizzard"
    mode.tick(world, [b1], 0.1)

    assert abs(b1.speed - (base_speed * 1.5)) < 0.01
    assert abs(b1.damage - (base_damage * 1.2)) < 0.01

    # Test non-winner
    b2 = MockBall("teamB", 0, 0)
    mode.setup(world, [b1, b2])

    mode.weather = "heatwave"
    mode.tick(world, [b1, b2], 0.1)

    assert abs(b2.speed - (b2.base_speed * 0.8)) < 0.01
    assert abs(b2.damage - (b2.base_damage * 1.0)) < 0.01
