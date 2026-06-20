from arena.arena_types import get_arena

def test_clutch_plays_arena_generation():
    arena = get_arena("clutch_plays", arena_size=1000.0)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 12

    # Check safe points (in rooms or corridors)
    cx, cy = 500.0, 500.0

    # Center room
    new_x, new_y, bounced = arena.clamp_position(cx, cy, 10.0)
    assert not bounced

    # Check outside bounds (e.g. corner)
    new_x, new_y, bounced = arena.clamp_position(50.0, 50.0, 10.0)
    assert bounced
