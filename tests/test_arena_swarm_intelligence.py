from arena.arena_types import SwarmIntelligenceArena

def test_swarm_intelligence_arena_layout():
    arena = SwarmIntelligenceArena(arena_size=2000.0, seed=42)

    # Check correct geometry counts
    assert len(arena.rooms) == 9
    assert len(arena.corridors) == 12
    assert len(arena.hazards) == 4

def test_swarm_intelligence_bounds():
    arena = SwarmIntelligenceArena(arena_size=2000.0, seed=42)

    # Point inside room (top-left room: 350, 350, 300, 300)
    assert arena.is_point_inside(500, 500, 10.0) is True

    # Point inside horizontal corridor (600, 450, 300, 100)
    assert arena.is_point_inside(700, 500, 10.0) is True

    # Point outside in the "negative space" (between rooms/corridors)
    assert arena.is_point_inside(700, 700, 10.0) is False
