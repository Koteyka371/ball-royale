import pytest
from unittest.mock import MagicMock, patch
from ai.game_modes import GAME_MODES

def test_invisible_mines_mode():
    mode = GAME_MODES.get("invisible_mines")
    assert mode is not None

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.hazards = []

    class _MockBall:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.alive = True

    b1 = _MockBall(1, 0, 0)
    balls = [b1]

    # First tick, initializes last_pos
    mode.tick(world, balls, delta=0.016)
    assert mode.last_pos[1] == (0, 0)
    assert mode.traveled[1] == 0.0
    assert len(world.arena.hazards) == 0

    # Second tick, moves a small amount
    b1.x = 100
    b1.y = 0
    mode.tick(world, balls, delta=0.016)
    assert mode.traveled[1] == 100.0
    assert len(world.arena.hazards) == 0

    # Third tick, moves enough to drop a mine, patch random to ensure it drops
    b1.x = 300
    b1.y = 0
    with patch("random.random", return_value=0.1):
        mode.tick(world, balls, delta=0.016)

    assert mode.traveled[1] == 100.0 # (100 + 200) - 200
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "hidden_mine"
    assert world.arena.hazards[0].x == 300
    assert world.arena.hazards[0].y == 0
