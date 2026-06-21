from arena.arena_types import Finals1v1Arena

def test_finals_1v1_arena_generation():
    arena = Finals1v1Arena(arena_size=2000.0)

    # Assert proper quantities
    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2
    assert len(arena.hazards) == 16

    cx, cy = arena.width / 2, arena.height / 2

    # Assert points inside rooms
    assert arena.is_point_inside(cx, cy, 10.0) # Central room
    assert arena.is_point_inside(cx - 650, cy, 10.0) # Left spawn
    assert arena.is_point_inside(cx + 450, cy, 10.0) # Right spawn

    # Assert points inside corridors
    assert arena.is_point_inside(cx - 400, cy, 10.0) # Left corridor
    assert arena.is_point_inside(cx + 400, cy, 10.0) # Right corridor

    # Assert points outside (bounding checks)
    assert not arena.is_point_inside(50, 50, 10.0)
    assert not arena.is_point_inside(arena.width - 50, 50, 10.0)
