import math
import pytest
import sys
sys.path.append('src')
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.weather = "clear"
        self.temperature = 20.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.radius = 15.0
        self.freeze_timer = 0.0
        self.stun_timer = 0.0
        self.ball_type = "basic"

    def take_damage(self, amount):
        self.hp = max(0.0, self.hp - amount)

def test_quantum_entanglement_hazards():
    mode = GAME_MODES['quantum_entanglement_hazards']
    world = MockWorld()

    b1 = MockBall(1, 250, 500)
    b2 = MockBall(2, 750, 500)
    b3 = MockBall(3, 500, 500) # Unaffected ball
    balls = [b1, b2, b3]

    mode.setup(world, balls)
    assert len(world.arena.hazards) == 2

    # Tick to initialize previous values
    mode.tick(world, balls, 0.016)

    # Damage b1, b2 should take 50% damage
    b1.take_damage(20.0)
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0
    assert b2.hp == 90.0 # 100 - (20 * 0.5)
    assert b3.hp == 100.0 # Unaffected

    # Status effect on b2, b1 should get 50%
    b2.freeze_timer = 4.0
    mode.tick(world, balls, 0.016)
    assert b2.freeze_timer == 4.0
    assert b1.freeze_timer == 2.0
    assert b3.freeze_timer == 0.0

    # Balls leaving zone should not take duplicated damage anymore
    b1.x = 500
    b1.y = 100
    mode.tick(world, balls, 0.016) # Leaves zone and updates prev_hp

    b2.take_damage(10.0)
    mode.tick(world, balls, 0.016)

    assert b2.hp == 80.0
    assert b1.hp == 80.0 # b1 was out of zone, should not take damage

def test_quantum_entanglement_stun():
    mode = GAME_MODES['quantum_entanglement_hazards']
    world = MockWorld()

    b1 = MockBall(1, 250, 500)
    b2 = MockBall(2, 750, 500)
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.016)

    b1.stun_timer = 10.0
    mode.tick(world, balls, 0.016)
    assert b2.stun_timer == 5.0
