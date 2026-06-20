import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from arena.arena_types import get_arena

def test_kite_arena_generation():
    arena = get_arena("kite", arena_size=2000.0, seed=42)

    # Check that there is only one central large room
    assert len(arena.rooms) == 1

    room = arena.rooms[0]
    assert room.x == 50
    assert room.y == 50
    assert room.width == 1900
    assert room.height == 1900

    # Check that hazards exist
    assert len(arena.hazards) > 0

    # Check for central large hazard
    central_hazards = [h for h in arena.hazards if h.radius >= 200.0]
    assert len(central_hazards) == 1

    central_hazard = central_hazards[0]
    assert central_hazard.x == 1000.0
    assert central_hazard.y == 1000.0
    assert central_hazard.kind == "lava"

    # Check for outer small hazards
    outer_hazards = [h for h in arena.hazards if h.radius == 30.0]
    assert len(outer_hazards) == 12
    for hazard in outer_hazards:
        assert hazard.kind == "spikes"

if __name__ == "__main__":
    test_kite_arena_generation()
    print("KiteArena tests passed.")
