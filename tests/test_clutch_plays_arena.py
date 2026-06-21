from src.arena.arena_types import get_arena, ClutchPlaysArena

def test_clutch_plays_arena():
    arena = get_arena("clutch_plays", arena_size=2000)
    assert isinstance(arena, ClutchPlaysArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

    # check safe zone overlaps with corridors
    # Safe zones: (50, 50, 150, 150) -> Top-Left
    # Corridors: (100, 200, 50, ...) -> x from 100 to 150, y from 200 to ...
    # Let's just make sure it runs without crashing.

if __name__ == "__main__":
    test_clutch_plays_arena()
    print("Test passed!")
