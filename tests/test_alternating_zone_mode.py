import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import GAME_MODES

def test_alternating_zone_mode():
    mode = GAME_MODES["alternating_zone"]
    world = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000
    world.leaderboard_manager.data.get.return_value = 1
    world._deal_damage = MagicMock()
    b = MagicMock()
    b.x = 500
    b.y = 500
    b.hp = 50
    b.max_hp = 100
    b.alive = True
    b.ball_type = "player"
    mode.setup_done = False
    mode.setup(world, [b])
    assert mode.is_healing_phase == True
    mode.tick(world, [b], delta=1.0)
    assert b.hp > 50
    mode.tick(world, [b], delta=5.0)
    assert mode.is_healing_phase == False
    mode.tick(world, [b], delta=1.0)
    world._deal_damage.assert_called()
