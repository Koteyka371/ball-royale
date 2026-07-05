import pytest
from ai.game_modes import MazeSafeZoneMode

def test_dummy_game_modes_coverage():
    mode = MazeSafeZoneMode()
    assert mode.name == "Maze Safe Zone"
