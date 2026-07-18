import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0

    def take_damage(self, amount, source=None):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type_str, data):
        self.events.append((type_str, data))

def test_chain_reaction_mode():
    mode = GAME_MODES.get('chain_reaction')
    assert mode is not None
    assert mode.name == "Chain Reaction"

    world = MockWorld()
    ball1 = MockBall(1, 100, 100)
    ball2 = MockBall(2, 110, 110) # close enough for explosion
    ball3 = MockBall(3, 500, 500) # too far
    balls = [ball1, ball2, ball3]

    # Kill ball1
    ball1.hp = 0
    ball1.alive = False
    mode.on_ball_died(world, ball1, killer=ball3)

    assert len(mode.pending_explosions) == 1
    exp = mode.pending_explosions[0]
    assert exp["x"] == 100
    assert exp["y"] == 100
    assert exp["timer"] == 1.5
    assert exp["radius"] == 150.0
    assert exp["damage"] == 50.0

    # Advance time by 1.0s, explosion shouldn't happen yet
    mode.tick(world, balls, delta=1.0)
    assert len(mode.pending_explosions) == 1
    assert ball2.hp == 100.0

    # Advance time by another 0.6s to trigger explosion
    mode.tick(world, balls, delta=0.6)
    assert len(mode.pending_explosions) == 0

    # Ball2 should take damage (50)
    assert ball2.hp == 50.0
    assert ball2.alive

    # Ball3 shouldn't take damage (too far)
    assert ball3.hp == 100.0

    # Check event
    assert any(e[0] == "chain_explosion" for e in world.events)

    # Now let's trigger a chain reaction
    ball2.hp = 0
    ball2.alive = False
    mode.on_ball_died(world, ball2, killer=None)

    assert len(mode.pending_explosions) == 1
    exp = mode.pending_explosions[0]
    assert exp["x"] == 110
    assert exp["y"] == 110
