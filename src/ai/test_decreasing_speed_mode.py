from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_decreasing_speed_mode():
    mode = GAME_MODES["decreasing_speed"]

    class FakeWorld:
        def __init__(self):
            self.leaderboard_manager = MagicMock()
            self.leaderboard_manager.data.get.return_value = 1

        def add_event(self, event, data):
            pass

    world = FakeWorld()

    class FakeBall:
        def __init__(self, speed):
            self.alive = True
            self.speed = speed
            self.base_speed = speed
            self.max_speed = 500.0
            self.vx = 100.0
            self.vy = 100.0

    ball = FakeBall(400.0)
    balls = [ball]

    mode.setup(world, balls)

    # Tick with time = 0.016
    mode.tick(world, balls, 0.016)
    assert abs(ball.speed - 300.0) < 0.1, f"Expected ~300.0, got {ball.speed}"
    assert abs(ball.max_speed - 300.0) < 0.1, f"Expected ~300.0, got {ball.max_speed}"

    # Fast forward to 50s
    mode.elapsed_time = 50.0
    ball.speed = 400.0 # reset speed to test cap
    mode.tick(world, balls, 0.0)
    assert abs(ball.speed - 200.0) < 0.1, f"Expected ~200.0, got {ball.speed}"

    # Fast forward to 200s (cap should decrease to min_speed_cap = 50.0)
    mode.elapsed_time = 200.0
    ball.speed = 200.0
    mode.tick(world, balls, 0.0)
    assert abs(ball.speed - 50.0) < 0.1, f"Expected ~50.0, got {ball.speed}"

if __name__ == "__main__":
    test_decreasing_speed_mode()
