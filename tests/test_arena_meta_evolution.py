import pytest
from arena.arena_types import MetaEvolutionArena, ARENAS

def test_meta_evolution_arena_registration():
    assert "meta_evolution" in ARENAS
    assert ARENAS["meta_evolution"] == MetaEvolutionArena

def test_meta_evolution_arena_generation():
    arena = MetaEvolutionArena(arena_size=2000.0)

    # 1 central hub + 4 evolution chambers
    assert len(arena.rooms) == 5

    # 4 diagonal connectors
    assert len(arena.corridors) == 4

    # 4 hazards inside connectors
    assert len(arena.hazards) == 4

    cx = 1000.0
    cy = 1000.0

    # check central hub coordinates
    hub = arena.rooms[0]
    assert hub.x == cx - 200
    assert hub.y == cy - 200
    assert hub.width == 400
    assert hub.height == 400

    # check top-left chamber
    tl_chamber = arena.rooms[1]
    assert tl_chamber.x == cx - 700
    assert tl_chamber.y == cy - 700
    assert tl_chamber.width == 300
    assert tl_chamber.height == 300

    # check top-left corridor
    tl_corridor = arena.corridors[0]
    assert tl_corridor.x == cx - 450
    assert tl_corridor.y == cy - 450
    assert tl_corridor.width == 300
    assert tl_corridor.height == 300

    # check top-left hazard
    tl_hazard = arena.hazards[0]
    assert tl_hazard.x == cx - 300
    assert tl_hazard.y == cy - 300
    assert tl_hazard.radius == 50.0
    assert tl_hazard.kind == "fire"
    assert tl_hazard.damage == 20.0
