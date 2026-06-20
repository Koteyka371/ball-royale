import os
import sys

sys.path.insert(0, os.path.abspath('src'))

from arena.arena_types import get_arena

def test_battle_royale_arena():
    arena = get_arena("battle_royale", arena_size=2000.0)
    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 4

    assert arena.safe_zone_radius == 1400.0

    arena.update_zone(1, 1.0)
    assert arena.safe_zone_radius == 1390.0
