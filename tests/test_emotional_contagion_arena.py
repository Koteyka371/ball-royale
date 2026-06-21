import pytest
from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=2000.0)
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 6
    assert len(arena.hazards) == 0

    central_room = arena.rooms[0]
    assert central_room.width == 400
    assert central_room.height == 400
