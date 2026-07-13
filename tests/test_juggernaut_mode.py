import pytest
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

def test_juggernaut_mode():
    mode = GAME_MODES["juggernaut"]
    world = MagicMock()


    world.leaderboard_manager.data.get.return_value = 1

    class RealMock:
        pass

    b1 = RealMock()
    b1.id = "b1"
    b1.ball_type = "warrior"
    b1.alive = True
    b1.max_hp = 100
    b1.hp = 100
    b1.damage = 10
    b1.radius = 10
    b1.speed = 100
    b1.base_speed = 100
    b1.mass = 1

    b2 = RealMock()
    b2.id = "b2"
    b2.ball_type = "warrior"
    b2.alive = True
    b2.max_hp = 100
    b2.hp = 100
    b2.damage = 10
    b2.radius = 10
    b2.speed = 100
    b2.base_speed = 100
    b2.mass = 1

    b3 = RealMock()
    b3.id = "b3"
    b3.ball_type = "warrior"
    b3.alive = True
    b3.max_hp = 100
    b3.hp = 100
    b3.damage = 10
    b3.radius = 10
    b3.speed = 100
    b3.base_speed = 100
    b3.mass = 1

    balls = [b1, b2, b3]

    mode.setup(world, balls)

    assert b1.team == "Juggernaut"
    assert b2.team == "Hunters"
    assert b3.team == "Hunters"

    assert b1.max_hp == 1000
    assert b1.hp == 1000

    # Simulate Juggernaut death
    b1.alive = False
    b1.hp = 0
    b1.killer = "b2"

    mode.tick(world, balls, 0.1)

    assert b1.team == "Dead"
    assert b2.team == "Juggernaut"
    assert b2.max_hp == 1000  # 100 * 10.0 (uses base_max_hp now)
    assert b2.hp == 1000

    # Check Winner
    b1.team = "Dead"
    b2.team = "Juggernaut"
    b3.team = "Hunters"

    b1.alive = False
    b2.alive = True
    b3.alive = True

    assert mode.check_winner(world, balls) is None

    b3.alive = False
    assert mode.check_winner(world, balls) == "Juggernaut"

    b3.alive = True
    b2.alive = False
    assert mode.check_winner(world, balls) == "Hunters"
