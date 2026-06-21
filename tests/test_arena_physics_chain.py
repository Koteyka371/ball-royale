from arena.arena_types import PhysicsChainArena

def test_physics_chain_arena_generation():
    arena = PhysicsChainArena(arena_size=2000.0, num_rooms=5, seed=42)

    # Check 5 rooms (4 spawn + 1 center)
    assert len(arena.rooms) == 5

    # Check 4 corridors
    assert len(arena.corridors) == 8

    # Check 8 hazards (4 center + 4 corridor)
    assert len(arena.hazards) == 8

    # Ensure hazards are roughly in expected positions
    # Just check that center hazards exist
    w, h = arena.width, arena.height
    cx, cy = w/2, h/2
    center_hazards = [h for h in arena.hazards if h.damage == 30.0]
    assert len(center_hazards) == 4

    corridor_hazards = [h for h in arena.hazards if h.damage == 15.0]
    assert len(corridor_hazards) == 4

    # Test point inside logic
    assert arena.is_point_inside(cx, cy, 5.0)  # Inside central room
    assert arena.is_point_inside(cx - 50, cy - 250, 5.0)  # Inside top-left corridor
