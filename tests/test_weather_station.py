import pytest
from ai.game_modes import GAME_MODES

def test_weather_station_mode():
    mode = GAME_MODES["weather_station"]
    assert mode.name == "Weather Station"

    class MockArena:
        width = 1000
        height = 1000

    class MockWorld:
        arena = MockArena()

    class MockBall:
        def __init__(self, team, x, y):
            self.alive = True
            self.ball_type = "normal"
            self.team = team
            self.x = x
            self.y = y
            self.hp = 100
            self.mass = 1.0

        def take_damage(self, amount):
            self.hp -= amount

    world = MockWorld()
    b1 = MockBall("team1", 500, 500)
    b2 = MockBall("team2", 100, 100)
    balls = [b1, b2]

    mode.setup(world, balls)
    assert mode.station is None

    # Tick to spawn station
    mode.tick(world, balls, delta=10.0)
    assert mode.station is not None

    # Move b1 to station
    b1.x = mode.station["x"]
    b1.y = mode.station["y"]

    # Capture it
    mode.tick(world, balls, delta=6.0) # 6 * 20 = 120 progress -> captured

    assert mode.controlling_team == "team1"
    assert mode.active_weather in ["lightning", "wind"]
    assert mode.station is None

    # Test weather effects
    import random
    random.seed(42) # Try to force outcomes or just let it tick enough times
    for _ in range(100):
        mode.tick(world, balls, delta=0.016)
