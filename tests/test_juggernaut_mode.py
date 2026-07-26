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


def test_juggernaut_swap_timer():
    world = MagicMock()
    world.tick_timer = 1.0
    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1

    class RealMock:
        pass

    def create_ball(id_name):
        b = RealMock()
        b.id = id_name
        b.ball_type = "warrior"
        b.alive = True
        b.max_hp = 100
        b.hp = 100
        b.damage = 10
        b.radius = 10
        b.speed = 100
        b.base_speed = 100
        b.mass = 1
        return b

    b1 = create_ball("jugg1")
    b2 = create_ball("hunt1")
    b3 = create_ball("hunt2")

    balls = [b1, b2, b3]

    mode = GAME_MODES["juggernaut"]
    mode.setup(world, balls)

    jugg = [b for b in balls if getattr(b, "team", "") == "Juggernaut"][0]
    assert jugg == b1

    # Tick for 29 seconds, should not swap
    for _ in range(290):
        mode.tick(world, balls, 0.1)

    jugg2 = [b for b in balls if getattr(b, "team", "") == "Juggernaut"][0]
    assert jugg2 == b1

    # Tick for 1 more second, should swap
    for _ in range(11):
        mode.tick(world, balls, 0.1)

    # The old juggernaut should be hunter now
    # The new juggernaut should be one of the hunters
    juggernauts = [b for b in balls if getattr(b, "team", "") == "Juggernaut"]
    assert len(juggernauts) == 1
    assert juggernauts[0] != jugg
    assert getattr(jugg, "team", "") == "Hunters"
