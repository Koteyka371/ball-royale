import pytest
from ai.game_modes import AlternatingZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def _deal_damage(self, attacker, target, amount):
        target.hp -= amount

class MockBall:
    def __init__(self, hp, max_hp, alive=True, ball_type="player", x=500.0, y=500.0):
        self.hp = hp
        self.max_hp = max_hp
        self.alive = alive
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.in_healing_zone = False

def test_alternating_zone_healing():
    world = MockWorld()
    b1 = MockBall(50.0, 100.0)
    b2 = MockBall(50.0, 100.0, x=100.0, y=100.0) # Outside zone
    mode = AlternatingZoneMode()
    mode.setup(world, [b1, b2])

    assert mode.is_healing_phase == True
    mode.tick(world, [b1, b2], 1.0)

    assert b1.hp == 70.0 # 50 + 20
    assert b1.in_healing_zone == True
    assert b2.hp == 50.0 # Unchanged
    assert b2.in_healing_zone == False

def test_alternating_zone_damaging():
    world = MockWorld()
    b1 = MockBall(100.0, 100.0)
    b2 = MockBall(100.0, 100.0, x=100.0, y=100.0) # Outside zone
    mode = AlternatingZoneMode()
    mode.setup(world, [b1, b2])

    # Manually change phase to avoid massive delta damage
    mode.is_healing_phase = False

    mode.tick(world, [b1, b2], 1.0)
    assert mode.is_healing_phase == False

    assert b1.hp == 80.0 # 100 - 20
    assert b2.hp == 100.0 # Unchanged
