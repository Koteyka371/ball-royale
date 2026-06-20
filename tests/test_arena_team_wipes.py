from arena.arena_types import TeamWipesArena

def test_team_wipes_arena():
    arena = TeamWipesArena(arena_size=2000.0, num_rooms=5)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 20
