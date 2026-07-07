import pytest
from arena.procedural_arena import ProceduralArena, Hazard

def test_lightning_warning_to_strike():
    arena = ProceduralArena()
    arena.width = 1000
    arena.height = 1000
    arena.hazards = []

    # Spawn a warning
    warning = Hazard(id=1, x=500, y=500, radius=30.0, kind="lightning_warning", damage=0.0)
    warning.duration = 0.1
    arena.hazards.append(warning)

    # Tick with delta that expires it
    arena.update_zone(current_tick=1, delta=0.2)

    # The warning should be inactive, and a new strike should appear
    strikes = [h for h in arena.hazards if h.kind == "lightning_strike"]
    assert not warning.active
    assert len(strikes) == 1
    assert strikes[0].damage == 50.0
    assert strikes[0].duration in [0.5, 0.3]
    assert strikes[0].x == 500
    assert strikes[0].y == 500
    print("Success test_lightning_warning_to_strike")

if __name__ == "__main__":
    test_lightning_warning_to_strike()
