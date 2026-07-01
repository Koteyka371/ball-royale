import pytest
from arena.arena_types import SummerArena, WinterArena, AutumnArena, LavaArena, NeonArena

def test_summer_arena():
    arena = SummerArena()
    assert getattr(arena, "is_heatwave", False) is True

def test_winter_arena():
    arena = WinterArena()
    assert getattr(arena, "is_snowing", False) is True

def test_autumn_arena():
    arena = AutumnArena()
    assert getattr(arena, "is_windy", False) is True

def test_lava_arena():
    arena = LavaArena()
    assert getattr(arena, "is_lava_theme", False) is True

def test_neon_arena():
    arena = NeonArena()
    assert getattr(arena, "is_neon_theme", False) is True
