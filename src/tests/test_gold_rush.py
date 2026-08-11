
import pytest
from ai.game_modes import GAME_MODES

def test_gold_rush_mode_registered():
    assert "gold_rush" in GAME_MODES

def test_gold_rush_mechanics():
    mode = GAME_MODES["gold_rush"]

    class MockWorld:
        def __init__(self):
            class Arena:
                def __init__(self):
                    self.width = 1000
                    self.height = 1000
            self.arena = Arena()
            self.events = []
        def add_event(self, type, data):
            self.events.append({"type": type, "data": data})

    class MockBall:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.radius = 15.0
            self.speed = 100.0
            self.alive = True
            self.team = "Red"

    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)
    balls = [b1, b2]

    # Fast forward to spawn coin
    mode.coin_spawn_timer = 3.0
    mode.tick(world, balls, 0.016)

    assert len(mode.coins) == 1
    coin = mode.coins[0]

    # Move b1 to coin
    b1.x = coin["x"]
    b1.y = coin["y"]

    mode.tick(world, balls, 0.016)

    assert len(mode.coins) == 0
    assert b1.collected_coins == 1
    assert b1.radius > 15.0
    assert b1.speed < 100.0

    # Check win condition
    mode.time_limit = 0.0
    winner = mode.check_winner(world, balls)
    assert winner == "Red"
