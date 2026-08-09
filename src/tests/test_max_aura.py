import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, id, team, aura_scale, x, y, hp, max_hp):
        self.id = id
        self.team = team
        self.cosmetic_aura_scale = aura_scale
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.speed_multiplier = 1.0
        self.is_decoy = False

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.arena = None

def test_max_aura_healing_and_slow():
    ball1 = MockBall(1, "A", 3.0, 0, 0, 100, 100)
    ball2 = MockBall(2, "A", 1.0, 10, 0, 50, 100) # Ally in range
    ball3 = MockBall(3, "B", 1.0, 10, 0, 50, 100) # Enemy in range
    ball4 = MockBall(4, "A", 1.0, 500, 0, 50, 100) # Ally out of range

    world = MockWorld([ball1, ball2, ball3, ball4])
    action = Action(ball1, world)

    # Delta 1.0, expect 10 hp heal and 0.5 speed
    action.execute("idle", 1.0)

    assert ball1.speed_multiplier == 0.5
    assert ball2.hp == 60.0
    assert ball3.hp == 50.0
    assert ball4.hp == 50.0

def test_no_max_aura_healing_and_slow():
    ball1 = MockBall(1, "A", 2.9, 0, 0, 100, 100)
    ball2 = MockBall(2, "A", 1.0, 10, 0, 50, 100) # Ally in range

    world = MockWorld([ball1, ball2])
    action = Action(ball1, world)

    action.execute("idle", 1.0)

    assert ball1.speed_multiplier == 1.0
    assert ball2.hp == 50.0
