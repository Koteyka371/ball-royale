import pytest
from ai.game_modes import VehicularCombatMode

class MockBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, base_damage=10.0, speed=50.0):
        self.x = x
        self.y = y
        self.hp = hp
        self.base_damage = base_damage
        self.speed = speed
        self.alive = True
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_vehicular_combat_setup():
    mode = VehicularCombatMode()
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)
    assert hasattr(world, "vehicles")
    assert len(world.vehicles) == 3
    for v in world.vehicles:
        assert v["type"] in ["tank", "hovercraft"]
        assert v["hp"] > 0
        assert v["driver"] is None

def test_vehicular_combat_mounting_and_stats():
    mode = VehicularCombatMode()
    world = MockWorld()

    b = MockBall(x=100, y=100, base_damage=10.0, speed=50.0)
    balls = [b]

    mode.setup(world, balls)
    world.vehicles = [{
        "x": 100, "y": 100, "radius": 30.0, "type": "tank",
        "hp": 500.0, "max_hp": 500.0, "base_damage": 50.0, "speed": 80.0, "driver": None
    }]

    mode.tick(world, balls, 1.0)

    assert getattr(b, "mounted_vehicle", None) is not None
    assert b.base_damage == 50.0
    assert b.speed == 80.0

def test_vehicular_combat_damage_and_ejection():
    mode = VehicularCombatMode()
    world = MockWorld()

    b = MockBall(x=100, y=100, hp=100.0, base_damage=10.0, speed=50.0)
    balls = [b]

    mode.setup(world, balls)
    world.vehicles = [{
        "x": 100, "y": 100, "radius": 30.0, "type": "tank",
        "hp": 20.0, "max_hp": 500.0, "base_damage": 50.0, "speed": 80.0, "driver": None
    }]

    mode.tick(world, balls, 1.0)

    assert getattr(b, "mounted_vehicle", None) is not None

    # Simulate ball taking 30 damage, vehicle should absorb it and die
    b.hp -= 30.0
    mode.tick(world, balls, 1.0)

    # Vehicle was at 20 HP, took 30 damage -> destroyed
    assert getattr(b, "mounted_vehicle", None) is None
    assert getattr(b, "stun_timer", 0.0) > 0.0
    assert b.hp == 100.0 # Ball HP restored

def test_vehicular_combat_stun():
    mode = VehicularCombatMode()
    world = MockWorld()

    b = MockBall(x=100, y=100, hp=100.0, base_damage=10.0, speed=50.0)
    b.stun_timer = 1.0
    b.original_base_speed = 50.0
    balls = [b]

    mode.setup(world, balls)
    world.vehicles = []

    mode.tick(world, balls, 0.5)

    assert b.speed == 0.0
    assert b.stun_timer == 0.5

    mode.tick(world, balls, 0.5)

    assert b.speed == 50.0
    assert b.stun_timer == 0.0
