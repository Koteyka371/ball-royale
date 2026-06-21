import pytest
import math
from src.arena.arena_types import get_arena, FleeArena

def test_flee_arena():
    arena = get_arena("flee")

    assert isinstance(arena, FleeArena)

    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "lava"
    assert math.isclose(arena.hazards[0].x, arena.width / 2.0)
    assert math.isclose(arena.hazards[0].y, arena.height / 2.0)
