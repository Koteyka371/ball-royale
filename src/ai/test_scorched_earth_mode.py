import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES, ScorchedEarthMode

def test_scorched_earth_mode():
    assert "scorched_earth" in GAME_MODES
    mode = GAME_MODES["scorched_earth"]

    world = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000

    # Need mock leaderboard manager
    lbm = MagicMock()
    lbm.data = {"current_season": 1}
    world.leaderboard_manager = lbm

    class MockBall:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.hp = 100.0
            self.stamina = 100.0
            self.alive = True
            self.ball_type = "player"
            self.weather_immunity_timer = 0.0

        def take_damage(self, amount):
            self.hp -= amount

    b1 = MockBall(500, 500)
    b2 = MockBall(10, 10)

    mode.setup(world, [b1, b2])

    assert mode.zone_x == 500
    assert mode.zone_y == 500
    assert mode.zone_radius == 1000 / 1.5

    # Run the tick loop
    mode.tick(world, [b1, b2], delta=1.0)

    # b1 is in the center, shouldn't take damage
    assert b1.hp == 100
    assert b1.stamina == 100

    # b2 is outside
    assert b2.hp < 100
    assert b2.stamina < 100
