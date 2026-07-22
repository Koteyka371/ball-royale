import sys
import math
sys.path.insert(0, "src")

from unittest.mock import MagicMock
from ai.game_modes import GameMode, GAME_MODES

def test_radiation_windstorm_mode():
    mode = GAME_MODES.get("radiation_windstorm")
    assert mode is not None

    world = MagicMock()
    world.season = 1
    world.leaderboard_manager.data = {'current_season': 1}
    world.profile_manager = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000

    b1 = MagicMock()
    b1.alive = True
    b1.hp = 100
    b1.x = 500
    b1.y = 500
    b1.intangible = False
    b1.radius = 10

    b2 = MagicMock()
    b2.alive = True
    b2.hp = 100
    b2.x = 1050  # Outside
    b2.y = 500
    b2.intangible = False
    b2.radius = 10

    b2.take_damage = MagicMock()

    mode.setup(world, [b1, b2])

    mode.wind_angle = 0  # Force wind angle to 0 (moving right)

    # Tick with delta = 1
    mode.tick(world, [b1, b2], delta=1.0)

    # Check wind application
    assert b1.x == 500 + 400 * 1.0

    # Check radiation damage
    b2.take_damage.assert_called_once_with(50.0 * 1.0)

    # Tick 30 times
    mode.angle_timer = 0
    mode.tick(world, [b1, b2], delta=1.0)

    # We should have an event
    assert world.add_event.called
    args = world.add_event.call_args[0]
    assert args[0] == "wind_shift"
