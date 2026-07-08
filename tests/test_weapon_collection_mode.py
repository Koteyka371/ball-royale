import pytest
from ai.game_modes import WeaponCollectionMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_damage = 10.0
        self.damage = 10.0

def test_weapon_collection_setup():
    mode = WeaponCollectionMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall()

    mode.setup(world, [b1, b2])

    assert b1.base_damage == 0.0
    assert b1.damage == 0.0
    assert b2.base_damage == 0.0
    assert b2.damage == 0.0
    assert len(world.arena.hazards) == 0

def test_weapon_collection_spawn():
    mode = WeaponCollectionMode()
    world = MockWorld()
    b1 = MockBall(x=10.0, y=10.0)

    mode.setup(world, [b1])

    # Tick below threshold
    mode.tick(world, [b1], delta=1.0)
    assert len(world.arena.hazards) == 0

    # Tick over threshold
    mode.tick(world, [b1], delta=2.1)
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "weapon_drop"
    assert world.arena.hazards[0].active == True

def test_weapon_collection_pickup():
    mode = WeaponCollectionMode()
    world = MockWorld()
    b1 = MockBall(x=500.0, y=500.0)

    mode.setup(world, [b1])

    # Spawn a weapon exactly at ball's position
    class MockHazard:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.radius = 15.0
            self.kind = "weapon_drop"
            self.active = True

    h = MockHazard()
    world.arena.hazards.append(h)

    assert b1.base_damage == 0.0

    # Tick should cause pickup
    mode.tick(world, [b1], delta=0.1)

    assert h.active == False
    assert b1.base_damage == 10.0
    assert b1.damage == 10.0
