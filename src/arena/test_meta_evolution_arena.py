from arena.arena_types import MetaEvolutionArena
from arena.procedural_arena import ProceduralArena

def test_meta_evolution_arena_generation():
    arena = MetaEvolutionArena(arena_size=2000.0, num_rooms=5, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "spikes"
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

def test_meta_evolution_arena_spawn():
    arena = MetaEvolutionArena(arena_size=2000.0, num_rooms=5, seed=42)
    x, y = arena.get_random_spawn_point(10.0)
    assert arena.is_point_inside(x, y, 10.0)
