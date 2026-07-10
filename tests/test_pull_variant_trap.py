import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockEventList(list):
    def append(self, event):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = MockEventList()
        self.tick = 123
        self.time = 0
        self.next_id = 9999
        self.boosters = []
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball and getattr(b, "team", "") != getattr(ball, "team", "")]}

    def _deal_damage(self, owner, target):
        target.hp -= owner.damage

class MockHazard:
    def __init__(self, id, x, y, kind, radius=40.0, damage=10.0, owner_id=1):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = damage
        self.owner_id = owner_id
        self.duration = 10.0
        self.trap_variant = "normal"
        self.active = True

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0
        self.stun_timer = 0.0
        self.is_stunned = False
        self.team = "A"
        self.ball_type = "normal"
        self.speed = 0
        self.base_speed = 0
        self.is_flying = False

def test_pull_variant_trap():
    world = MockWorld()
    ball1 = MockBall(2, 50, 50)
    ball1.team = "B"
    owner_ball = MockBall(1, 0, 0)
    world.balls = [owner_ball, ball1]

    trap = MockHazard(1, 10, 10, "trap", radius=20.0, damage=10.0, owner_id=1)
    trap.trap_variant = "pull"
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    # move ball into trap
    ball1.x = 10
    ball1.y = 15
    action.execute("idle", 0.016)

    # Should transform into a pull_trap hazard
    assert trap.duration == 0.0
    pull_traps = [h for h in world.arena.hazards if getattr(h, "kind", "") == "gravity_well"]
    assert len(pull_traps) == 1
    pt = pull_traps[0]
    assert pt.x == 10
    assert pt.y == 10
    assert pt.duration == 4.0
    assert pt.radius == 200.0

if __name__ == "__main__":
    pytest.main(["-v", "test_pull_variant.py"])
