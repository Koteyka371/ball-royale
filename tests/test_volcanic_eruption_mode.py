import pytest
import sys
from unittest.mock import MagicMock
sys.path.append('src')

from ai.game_modes import GAME_MODES, GameMode

def test_volcanic_eruption_mode():
    mode = GAME_MODES.get('volcanic_eruption')
    assert mode is not None


    world = MagicMock()
    world.season = 1
    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data = {"current_season": 1}
    world.profile_manager = MagicMock()
    world.profile_manager.leaderboard_manager = world.leaderboard_manager
    world.arena = MagicMock()
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000
    world.events = []
    def add_event(type, data):
        world.events.append((type, data))
    world.add_event = add_event


    mode.setup(world, [])
    assert mode.eruption_timer == 0.0
    assert mode.is_erupting == False

    # Advance time to trigger eruption
    mode.tick(world, [], 15.0)
    assert mode.is_erupting == True
    assert len(world.events) > 0
    assert any(e[0] == "volcano_eruption_start" for e in world.events)

    # Advance time to drop projectile
    mode.tick(world, [], 0.6)
    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[0].kind == "lava_puddle"

    # Advance time to end eruption
    mode.tick(world, [], 4.5)
    assert mode.is_erupting == False
