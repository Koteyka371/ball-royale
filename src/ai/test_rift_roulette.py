import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_rift_roulette_spawns_portals():
    mode = GAME_MODES["rift_roulette"]
    world = MockWorld()
    balls = []

    # Trigger tick
    mode.tick(world, balls, delta=9.0)  # > 8.0 cycle interval

    # Should have portals and maybe hazards
    portals = [h for h in world.arena.hazards if getattr(h, "is_rift_portal", False)]

    # 2 pairs = 4 portals
    assert len(portals) == 4

    # Ensure they are linked properly
    for p in portals:
        assert p.kind == "teleporter"
        assert hasattr(p, "target_x")
        assert hasattr(p, "target_y")

    # Should have some hazards with is_rift_hazard
    rift_hazards = [h for h in world.arena.hazards if getattr(h, "is_rift_hazard", False)]
    # Random, might be 0, but check the flag
    for h in rift_hazards:
        assert h.duration == 5.0

    assert any(e[0] == "rifts_shifted" for e in world.events)

if __name__ == '__main__':
    pytest.main([__file__])
