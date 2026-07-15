import pytest
from unittest.mock import MagicMock

def test_elastic_band_hazard_logic():
    from ai.game_modes import ElasticBandHazardMode
    mode = ElasticBandHazardMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1

    b1 = MagicMock()
    b1.id = 1
    b1.hp = 100
    b1.x, b1.y = 400, 500
    b1.vx, b1.vy = 200, 0

    balls = [b1]
    mode.setup(world, balls)

    # Enters zone
    mode.tick(world, balls, 0.1)
    assert 1 in mode.grabbed
    assert mode.grabbed[1]["phase"] == "stretching"

    # Tick simulation
    for _ in range(15):
        b1.x += b1.vx * 0.1
        b1.y += b1.vy * 0.1
        mode.tick(world, balls, 0.1)

    # Eventually launched and removed from zone tracking because it flies far out
    assert 1 not in mode.grabbed
    assert b1.vx < -100 # violently launched back
