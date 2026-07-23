import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = "player"
        self.hp = 100
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.in_corruption_zone = False

    def take_damage(self, amount, source=None):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.next_id = 1

    def add_event(self, name, data):
        self.events.append([name, data])

def test_corruption_zone():
    mode = GAME_MODES["corruption_zone"]
    world = MockWorld()

    # Place one ball in center, one far away
    b1 = MockBall(500, 500)
    b2 = MockBall(100, 100)
    balls = [b1, b2]

    mode.setup(world, balls)
    assert len(mode.zones) == 0

    # Tick until zone spawns
    for _ in range(100):
        mode.tick(world, balls, 0.1)
        if len(mode.zones) > 0:
            break

    assert len(mode.zones) == 1
    zone = mode.zones[0]
    zone["timer"] = 0 # force active immediately

    # Move b1 into zone, b2 out of zone
    b1.x = zone["x"]
    b1.y = zone["y"]

    b2.x = zone["x"] + zone["radius"] + 50
    b2.y = zone["y"] + zone["radius"] + 50

    mode.tick(world, balls, 1.0)
    mode.tick(world, balls, 1.0)

    # b1 should have taken damage and gained buffs
    assert b1.hp < 100
    assert b1.damage > 20
    assert b1.speed > 250
    assert b1.in_corruption_zone == True

    # b2 should be untouched
    assert b2.hp == 100
    assert b2.damage == b2.base_damage
    assert b2.speed == b2.base_speed
    assert b2.in_corruption_zone == False

    # Now let zone expire
    zone["timer"] = -0.1
    mode.tick(world, balls, 1.0)
    mode.tick(world, balls, 1.0)

    # b1 should lose buffs
    assert b1.in_corruption_zone == False
    assert b1.damage <= 20
    assert b1.speed <= 150
