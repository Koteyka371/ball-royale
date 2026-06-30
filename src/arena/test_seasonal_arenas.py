import pytest
from arena.arena_types import SummerArena, WinterArena

def test_summer_arena():
    arena = SummerArena()
    assert getattr(arena, "is_heatwave", False) is True

def test_winter_arena():
    arena = WinterArena()
    assert getattr(arena, "is_snowing", False) is True
