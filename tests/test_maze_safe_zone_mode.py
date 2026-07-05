import pytest
from ai.game_modes import MazeSafeZoneMode

def test_maze_safe_zone_mode_exists():
    mode = MazeSafeZoneMode()
    assert mode.name == "Maze Safe Zone"
