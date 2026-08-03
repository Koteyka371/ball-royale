import pytest
import sys
import os

# Add src to the PYTHONPATH correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []
        self.width = 1000.0
        self.height = 1000.0
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 1000.0

    def clamp_position(self, x, y, radius):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls or []
        self.arena = arena or MockArena()
        self.events = []
        self.next_id = 1000

    def _deal_damage(self, attacker, target, damage, damage_type="normal", knockback=0.0):
        target.hp -= damage

class MockBall:
    def __init__(self, id_val, team="blue"):
        self.id = id_val
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 10.0
        self.base_speed = 10.0
        self.radius = 10.0
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.hologram_clones = []
        self._last_dx = 0.0
        self._last_dy = 0.0

class MockHazard:
    def __init__(self, x, y, kind="trap", trap_variant="swap", radius=15.0, owner_id=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.trap_variant = trap_variant
        self.radius = radius
        self.duration = 5.0
        self.owner_id = owner_id
        self.owner_team = "blue"

def test_swap_trap_trigger():
    trapper = MockBall(1, "blue")
    trapper.x = 100.0
    trapper.y = 100.0

    victim = MockBall(2, "red")
    victim.x = 200.0
    victim.y = 200.0

    # Trap placed by trapper
    trap = MockHazard(x=200.0, y=200.0, owner_id=trapper.id)
    trap.radius = 15.0
    trap.kind = "trap"
    trap.trap_variant = "swap"

    arena = MockArena([trap])
    world = MockWorld([trapper, victim], arena)

    # Initialize action for victim
    action = Action(victim, world)

    # We call action.execute, giving it "idle" strategy.
    # We also prevent the victim from moving normally to ensure clean swap testing.
    victim.speed = 0.0
    victim.base_speed = 0.0

    action.execute("idle", 0.1)

    # They should have swapped positions (allow small floating point variance)
    assert abs(victim.x - 100.0) < 5.0
    assert abs(victim.y - 100.0) < 5.0
    assert abs(trapper.x - 200.0) < 5.0
    assert abs(trapper.y - 200.0) < 5.0

    # Trap should be destroyed
    assert getattr(trap, "duration", 10.0) == 0.0

if __name__ == "__main__":
    pytest.main([__file__])
