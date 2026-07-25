import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, name="TestBall"):
        self.name = name
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 100.0
        self.is_alive = True
        self.alive = True
        self.hp = 100.0
        self.team = "TeamA"
        self.kinetic_momentum_time = 0.0

def test_kinetic_momentum_mutator():
    mutator = GAME_MODES["kinetic_momentum_mutator"]
    world = MockWorld()

    b1 = MockBall("B1")
    b2 = MockBall("B2")
    b2.team = "TeamB"
    b2.x = 50.0
    b3 = MockBall("B3")
    b3.team = "TeamA" # ally of B1
    b3.x = 250.0

    world.balls = [b1, b2, b3]

    # Tick with B1 not moving fast enough
    b1.vx = 80.0 # hypot is 80.0 < 90.0 (90% of base_speed)
    mutator.tick(world, world.balls, 1.0)
    assert getattr(b1, "kinetic_momentum_time", 0.0) == 0.0

    # Tick with B1 moving fast
    b1.vx = 95.0
    mutator.tick(world, world.balls, 2.0)
    assert getattr(b1, "kinetic_momentum_time", 0.0) == 2.0

    # B1 hits B2, does bonus damage
    mutator.on_damage_dealt(world, b1, b2, 10.0)
    # bonus damage = 10.0 * (3.0 - 1.0) * (2.0 / 5.0) = 20.0 * 0.4 = 8.0
    assert b2.hp == 100.0 - 8.0 # 92.0
    assert b1.kinetic_momentum_time == 0.0

    # Tick to get max time
    b1.vx = 100.0
    mutator.tick(world, world.balls, 6.0)
    assert b1.kinetic_momentum_time == 6.0

    # B1 hits B2 again, max bonus damage and AoE
    b2.hp = 100.0
    mutator.on_damage_dealt(world, b1, b2, 10.0)
    # bonus damage = 10.0 * 2.0 * 1.0 = 20.0
    assert b2.hp == 100.0 - 20.0 # 80.0
    # Blast damage on B2? Wait, does AoE hit target?
    # No, condition in on_damage_dealt: b != attacker and b != target
    # Wait, B2 is the target, so it shouldn't take blast damage.
    assert len(world.events) == 1
    assert world.events[0]["type"] == "kinetic_blast"

    # What if there's an enemy nearby
    b4 = MockBall("B4")
    b4.team = "TeamB"
    b4.x = 50.0
    world.balls.append(b4)

    b1.vx = 100.0
    mutator.tick(world, world.balls, 5.0)
    mutator.on_damage_dealt(world, b1, b2, 10.0)
    assert b4.hp == 50.0 # took 50 blast damage
    assert b3.hp == 100.0 # B3 is ally, no damage
