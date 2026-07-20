import pytest
import sys
sys.path.append('src')
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.balls = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, kind, x, y, hp=200):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 20
        self.hp = hp
        self.max_hp = hp
        self.damage = 50
        self.speed = 40

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0
        self.y = 0
        self.speed = 100
        self.base_speed = 100
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.base_damage = 10
        self.alive = True

def test_vehicle_mount():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    hazard = MockHazard('vehicle_mount', 0, 0, 200)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("offensive", 0.1)

    assert getattr(ball, 'is_mounted', False)
    assert ball.hp == 200
    assert hazard not in world.arena.hazards

    action.execute("offensive", 0.1)

    ball.hp = 0
    action.execute("offensive", 0.1)

    assert not getattr(ball, 'is_mounted', False)
    assert getattr(ball, 'stutter_timer', 0.0) >= 1.9
