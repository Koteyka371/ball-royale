import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arena.arena_types import BallGeneticsArena

def test_ball_genetics_arena_generation():
    arena = BallGeneticsArena(arena_size=2000.0, seed=42)
    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 8
    assert len(arena.hazards) == 5

    spikes = [h for h in arena.hazards if h.kind == "spikes"]
    lava = [h for h in arena.hazards if h.kind == "lava"]
    assert len(spikes) == 4
    assert len(lava) == 1
