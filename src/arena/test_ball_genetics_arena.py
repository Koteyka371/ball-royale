import pytest
from arena.arena_types import BallGeneticsArena, ARENAS

def test_ball_genetics_arena_registered():
    assert "ball_genetics" in ARENAS
    assert ARENAS["ball_genetics"] == BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = BallGeneticsArena(arena_size=2000.0, num_rooms=5, seed=42)

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    # Check that rooms have valid dimensions
    for r in arena.rooms:
        assert r.width > 0
        assert r.height > 0

    # Check that corridors have valid dimensions
    for c in arena.corridors:
        assert c.width > 0
        assert c.height > 0

    # Check that hazards are correct
    lava_hazards = [h for h in arena.hazards if h.kind == "lava"]
    spike_hazards = [h for h in arena.hazards if h.kind == "spikes"]
    assert len(lava_hazards) == 1
    assert len(spike_hazards) == 4
