import pytest
from ai.game_modes import GameMode, GAME_MODES
from ai.action import Action

class MockBall:
    def __init__(self, id, x=0, y=0, radius=10):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.stun_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []

def test_resonance_chain_mirror_damage():
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    balls = [b1, b2, b3]

    mode = GAME_MODES["resonance_chain"]
    mode.setup(world, balls)

    # Initial state
    assert b1.hp == 100.0
    assert b2.hp == 100.0
    assert b3.hp == 100.0

    # b1 takes 20 damage
    b1.hp = 80.0
    mode.tick(world, balls, 0.1)

    # b2 and b3 should also take 20 damage
    assert b2.hp == 80.0
    assert b3.hp == 80.0

    # b2 takes 10 damage
    b2.hp = 70.0
    mode.tick(world, balls, 0.1)

    # b1 and b3 should take 10 damage
    assert b1.hp == 70.0
    assert b3.hp == 70.0

    # b3 takes fatal damage
    b3.hp = -10.0
    mode.tick(world, balls, 0.1)

    # b1 and b2 should also die
    assert b1.hp == 0.0
    assert b2.hp == 0.0
    assert not b1.alive
    assert not b2.alive
    assert not b3.alive
