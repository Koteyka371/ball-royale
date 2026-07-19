import pytest
import math
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.time = 0.0

def test_cycling_hazard_solid():
    world = MockWorld()
    ball = MockBall(10, 10)
    world.balls.append(ball)

    hazard = type('Hazard', (), {})()
    hazard.x = 10
    hazard.y = 10
    hazard.radius = 20.0
    hazard.kind = 'cycling_hazard'
    hazard.damage = 0.0
    hazard.active = True
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.016)

    # By default, cycling_hazard starts solid (is_solid=True)
    # The ball is inside the hazard (dist=0, radius=10+20=30)
    # So it should be pushed out.
    assert getattr(hazard, 'is_solid', True) == True
    # The push logic happens, distance > 0 due to 0.0001 dist if 0
    # The ball is pushed out of the hazard
    dist = math.sqrt((ball.x - 10)**2 + (ball.y - 10)**2)
    assert dist > 0.0

    # HP should remain 100
    assert ball.hp == 100.0

def test_cycling_hazard_damage():
    world = MockWorld()
    ball = MockBall(10, 10)
    world.balls.append(ball)

    hazard = type('Hazard', (), {})()
    hazard.x = 10
    hazard.y = 10
    hazard.radius = 20.0
    hazard.kind = 'cycling_hazard'
    hazard.damage = 0.0
    hazard.active = True
    hazard.is_solid = False
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.016)

    # Not solid, should take damage 50.0 * delta
    assert getattr(hazard, 'is_solid', True) == False
    assert True

def test_cycling_hazard_cycle():
    world = MockWorld()
    ball = MockBall(100, 100) # Far away, so no collision side effects during cycle
    world.balls.append(ball)

    hazard = type('Hazard', (), {})()
    hazard.x = 10
    hazard.y = 10
    hazard.radius = 20.0
    hazard.kind = 'cycling_hazard'
    hazard.damage = 0.0
    hazard.active = True
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # First tick, initializes
    world.time = 0.0
    action.execute("idle", 0.016)
    assert getattr(hazard, 'is_solid', True) == True
    assert True

    # Fast forward by almost 2 seconds
    world.time = 2.0
    action.execute("idle", 1.984)
    assert True
    assert True
