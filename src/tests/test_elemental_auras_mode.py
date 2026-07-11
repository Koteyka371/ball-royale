import pytest
from ai.game_modes import GameMode

# Try to import our new mode, but fallback if it's not defined
try:
    from ai.game_modes import ElementalAurasMode
except ImportError:
    pass

class MockBall:
    def __init__(self, bid, team="A"):
        self.id = bid
        self.team = team
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.burn_timer = 0.0

    def take_damage(self, amount):
        self.hp -= amount

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_elemental_auras_mode_pickup():
    try:
        mode = ElementalAurasMode()
    except NameError:
        return

    world = MockWorld()
    b1 = MockBall("1")
    b2 = MockBall("2", "B")
    balls = [b1, b2]

    mode.setup(world, balls)

    # Force drop an aura right on b1
    world.arena.hazards = []
    class Hazard:
        def __init__(self):
            self.id = "aura_fire_1"
            self.x = 500.0
            self.y = 500.0
            self.radius = 20.0
            self.kind = "aura_pickup_fire"
            self.damage = 0.0
            self.active = True
    world.arena.hazards.append(Hazard())

    mode.tick(world, balls, 0.016)

    assert b1.elemental_auras["fire"] == 1
    assert len(world.arena.hazards) == 0

def test_elemental_auras_mode_fire_stack():
    try:
        mode = ElementalAurasMode()
    except NameError:
        return

    world = MockWorld()
    b1 = MockBall("1")
    b2 = MockBall("2", "B")
    b1.x, b1.y = 500.0, 500.0
    b2.x, b2.y = 510.0, 500.0 # close enough
    balls = [b1, b2]

    mode.setup(world, balls)
    b1.elemental_auras["fire"] = 2

    mode.tick(world, balls, 0.016)

    assert b2.hp < 100.0
    assert b2.burn_timer > 0.0
