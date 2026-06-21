from arena.arena_types import get_arena, BallGeneticsArena

def test_ball_genetics_arena():
    arena = get_arena("ball_genetics", arena_size=2000)
    assert isinstance(arena, BallGeneticsArena)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 4

if __name__ == "__main__":
    test_ball_genetics_arena()
    print("Test passed!")
