import pytest
from arena.arena_types import EmotionalContagionArena

def test_emotional_contagion_arena_generation():
    arena = EmotionalContagionArena(arena_size=1000.0)
    arena.generate()

    assert len(arena.rooms) == 5
    assert len(arena.corridors) == 4
    assert len(arena.hazards) == 5

    # Center Room
    assert arena.rooms[0].width == 400
    assert arena.rooms[0].height == 400

    # Corner Rooms
    assert arena.rooms[1].width == 300
    assert arena.rooms[1].height == 300

    # Corridors
    assert arena.corridors[0].width == 300
    assert arena.corridors[0].height == 300

    # Hazards
    assert arena.hazards[0].radius == 100.0
    assert arena.hazards[1].radius == 50.0
    assert arena.hazards[2].radius == 50.0
