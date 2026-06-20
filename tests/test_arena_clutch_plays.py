from arena.arena_types import ClutchPlaysArena

def test_clutch_plays_arena_generation():
    arena = ClutchPlaysArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 1
    assert len(arena.corridors) == 0
    assert len(arena.hazards) == 16

    # Verify the bounds
    room = arena.rooms[0]
    assert room.x == 100
    assert room.y == 100
    assert room.width == 1800
    assert room.height == 1800

    # Verify a few hazards
    hazard = arena.hazards[0]
    assert hazard.kind == "spikes"
    assert hazard.radius == 50.0
    assert hazard.damage == 99.0
