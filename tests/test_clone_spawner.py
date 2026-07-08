import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.action import Action

class MockHazard:
    def __init__(self, x, y, radius, kind="clone_spawner", active=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = active

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard(100, 100, 40.0)]
        self.platforms = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.dead_balls = []

    def _deal_damage(self, attacker, target, damage=None):
        pass

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.team = "A"
        self.alive = True
        self.is_decoy = False
        self.is_hostile_clone = False
        self.radius = 10.0
        self.perception_radius = 100.0
        self.base_speed = 2.0
        self.speed = 2.0
        self.vx = 0.0
        self.vy = 0.0

    def copy(self):
        import copy
        return copy.copy(self)

def test_clone_spawner_triggers():
    world = MockWorld()
    ball = MockBall(1, 100, 100)  # Inside spawner radius
    world.balls.append(ball)

    action = Action(ball, world)

    # Should trigger
    action.execute("none", 0.1)

    assert world.arena.hazards[0].active == False
    assert len(world.balls) == 2

    clone = world.balls[1]
    assert clone.team == "hostile_clones"
    assert clone.is_hostile_clone == True
    assert clone.is_decoy == False
    assert clone.id != ball.id

    assert len(world.events) == 1
    assert world.events[0][0] == "clone_spawner_trigger"

def test_clone_spawner_no_trigger_if_outside():
    world = MockWorld()
    ball = MockBall(1, 200, 200)  # Outside spawner radius
    world.balls.append(ball)

    action = Action(ball, world)

    # Should not trigger
    action.execute("none", 0.1)

    assert world.arena.hazards[0].active == True
    assert len(world.balls) == 1
    assert len(world.events) == 0

def test_clone_spawner_no_trigger_if_inactive():
    world = MockWorld()
    world.arena.hazards[0].active = False
    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    action = Action(ball, world)

    # Should not trigger
    action.execute("none", 0.1)

    assert len(world.balls) == 1
    assert len(world.events) == 0
