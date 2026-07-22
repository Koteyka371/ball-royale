import pytest
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.name = "TestArena"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, hp=100.0, speed=100.0, damage=10.0, traits=None, alive=True):
        self.id = id
        self.hp = hp
        self.max_hp = 100.0
        self.speed = speed
        self.base_speed = speed
        self.damage = damage
        self.base_damage = damage
        self.traits = traits or []
        self.alive = alive
        self.ball_type = "base"
        self.x = 0.0
        self.y = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

def test_quantum_entangled_setup_even():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(1, traits=["quantum_entangled"])
    b2 = MockBall(2, traits=["quantum_entangled"])
    b3 = MockBall(3) # Not entangled

    balls = [b1, b2, b3]
    mode.setup(world, balls)

    assert getattr(b1, "quantum_entangled_partner", None) == b2
    assert getattr(b2, "quantum_entangled_partner", None) == b1
    assert getattr(b3, "quantum_entangled_partner", None) is None
    assert b1.quantum_prev_hp == 100.0
    assert b2.quantum_prev_hp == 100.0

def test_quantum_entangled_setup_odd():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(1, traits=["quantum_entangled"])
    b2 = MockBall(2)

    balls = [b1, b2]
    mode.setup(world, balls)

    assert getattr(b1, "quantum_entangled_partner", None) == b2
    assert getattr(b2, "quantum_entangled_partner", None) == b1
    assert "quantum_entangled" in b2.traits

def test_quantum_entangled_damage_sharing():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(1, traits=["quantum_entangled"])
    b2 = MockBall(2, traits=["quantum_entangled"])
    balls = [b1, b2]
    mode.setup(world, balls)

    # Simulate damage on b1
    b1.take_damage(20) # b1 HP goes to 80
    mode.tick(world, balls, 0.016)

    # b2 should take 50% of 20 = 10 damage
    assert b1.hp == 80.0
    assert b2.hp == 90.0

    # Next tick with no changes should not recursively damage
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0
    assert b2.hp == 90.0

def test_quantum_entangled_healing_sharing():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(1, hp=50.0, traits=["quantum_entangled"])
    b2 = MockBall(2, hp=50.0, traits=["quantum_entangled"])
    balls = [b1, b2]
    mode.setup(world, balls)

    # Simulate healing on b1
    b1.hp += 30 # b1 HP goes to 80
    mode.tick(world, balls, 0.016)

    # b2 should heal 50% of 30 = 15
    assert b1.hp == 80.0
    assert b2.hp == 65.0

    # Next tick with no changes
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0
    assert b2.hp == 65.0

def test_quantum_entangled_enraged_state():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(1, traits=["quantum_entangled"])
    b2 = MockBall(2, traits=["quantum_entangled"])
    balls = [b1, b2]
    mode.setup(world, balls)

    # b2 dies
    b2.take_damage(100)
    assert b2.alive == False

    mode.tick(world, balls, 0.016)

    # b1 should become enraged (speed and damage * 2.0)
    assert b1.quantum_enraged == True
    assert b1.speed == 240.0
    assert b1.damage == 20.0

    # Check visual effect event
    events = [e for e in world.events if e[0] == "visual_effect" and e[1].get("type") == "quantum_enrage"]
    assert len(events) > 0
