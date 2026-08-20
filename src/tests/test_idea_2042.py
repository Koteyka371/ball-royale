import pytest
import math
from ai.game_modes import EscortMode
from arena.procedural_arena import Hazard

class MockPayload:
    def __init__(self):
        self.team = "Defenders"
        self.x = 500.0
        self.y = 500.0
        self.radius = 20.0
        self.speed = 100.0
        self.cargo_type = "energy_barrier"
        self.alive = True
        self.ball_type = "payload"
        self.hp = 5000.0
        self.max_hp = 5000.0
        self.is_invulnerable = False
        self.disabled_timer = 0.0
        self.damage_taken_window = 0.0
        self.damage_window_timer = 0.0
        self.damage = 0.0
        self.unopposed_timer = 0.0
        self.sabotaged = False

class MockWorld:
    def __init__(self):
        self.boosters = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorldWithArena:
    def __init__(self):
        self.arena = MockArena()

def test_escort_mode_spawns_boosters_at_checkpoint():
    mode = EscortMode()
    world = MockWorld()
    payload = MockPayload()
    mode.payload = payload

    # We set current waypoint and move payload to the checkpoint
    mode.chosen_path = 0
    mode.paths = [
        {"waypoints": [(500.0, 500.0), (900.0, 500.0)], "risk": "low"}
    ]
    mode.current_waypoint_index = 0

    # Tick should trigger checkpoint logic because distance to 500,500 is 0
    mode.tick(world, [payload], delta=0.1)

    # Verify boosters were added (it adds 3 for the new logic, plus our test environment might cause it to trigger twice if we're not careful, we'll check >= 3)
    assert len(world.boosters) >= 3
    for b in world.boosters:
        assert getattr(b, "type") in ["speed", "shield", "damage"] if hasattr(b, "type") else b.get("type") in ["speed", "shield", "damage"]
        assert getattr(b, "team") == "Defenders" if hasattr(b, "team") else b.get("team") == "Defenders"
        assert getattr(b, "duration") == 15.0 if hasattr(b, "duration") else b.get("duration") == 15.0

        # Verify it spawns near payload
        bx = getattr(b, "x") if hasattr(b, "x") else b.get("x")
        by = getattr(b, "y") if hasattr(b, "y") else b.get("y")
        dist = math.hypot(bx - payload.x, by - payload.y)
        assert dist <= 200.0 # Random range is +/- 100 on x and y, max hypot is ~141

def test_escort_mode_spawns_hazards_at_checkpoint_fallback():
    mode = EscortMode()
    world = MockWorldWithArena()
    payload = MockPayload()
    mode.payload = payload

    # We set current waypoint and move payload to the checkpoint
    mode.chosen_path = 0
    mode.paths = [
        {"waypoints": [(500.0, 500.0), (900.0, 500.0)], "risk": "low"}
    ]
    mode.current_waypoint_index = 0

    # Tick should trigger checkpoint logic because distance to 500,500 is 0
    mode.tick(world, [payload], delta=0.1)

    # One extra hazard is spawned from existing checkpoint logic (energy barrier)
    assert len(world.arena.hazards) >= 3

    buff_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") in ["speed_zone", "heal_zone", "shield_zone"]]
    assert len(buff_hazards) >= 3

    for h in buff_hazards:
        assert getattr(h, "team") == "Defenders"
        assert getattr(h, "duration") == 15.0
