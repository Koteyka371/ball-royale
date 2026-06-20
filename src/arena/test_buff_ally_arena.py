import sys
sys.path.insert(0, 'src')
from arena.arena_types import BuffAllyArena

def test_buff_ally_arena():
    arena = BuffAllyArena(arena_size=2000.0)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
