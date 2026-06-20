import sys
sys.path.insert(0, 'src')
from arena.arena_types import ARENAS, get_arena
from arena.procedural_arena import ProceduralArena

def test_target_strong_arena_registered():
    assert "target_strong" in ARENAS
    arena = get_arena("target_strong", 2000.0)
    assert isinstance(arena, ProceduralArena)
    assert type(arena).__name__ == "TargetStrongArena"

def test_target_strong_arena_generation():
    arena = get_arena("target_strong", 2000.0)
    # 1 center + 4 corners = 5 rooms
    assert len(arena.rooms) == 5
    # 2 corridors per corner = 8 corridors
    assert len(arena.corridors) == 8

    # Check bounds
    for r in arena.rooms:
        assert r.x >= 0
        assert r.y >= 0
        assert r.x + r.width <= arena.width
        assert r.y + r.height <= arena.height

    for c in arena.corridors:
        assert c.x >= 0
        assert c.y >= 0
        assert c.x + c.width <= arena.width
        assert c.y + c.height <= arena.height
