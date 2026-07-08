import pytest
from arena.arena_types import get_arena, SpringArena

def test_spring_arena_generation():
    arena = get_arena("spring", arena_size=1000.0)
    assert isinstance(arena, SpringArena)

    bounce_pads = [h for h in arena.hazards if getattr(h, "kind", "") == "bounce_pad"]
    assert len(bounce_pads) >= 15

    for pad in bounce_pads:
        assert pad.damage == 0.0
        assert pad.x >= 0 and pad.x <= arena.width
        assert pad.y >= 0 and pad.y <= arena.height
