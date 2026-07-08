import pytest
from ai.action import Action
import random

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.duration = 10.0
        self.x = 100
        self.y = 100
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockEventList(list):
    def append(self, event):
        pass

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0
        self.next_id = 9999
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball and getattr(b, "team", "") != getattr(ball, "team", "")]}

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = team
        self.alive = True
        self.is_decoy = False
        self.radius = 10
        self.speed = 0
        self.base_speed = 0
        self.is_flying = False

def test_swap_trap_prioritizes_enemy():
    random.seed(42)
    trap = MockHazard("swap_trap")
    arena = MockArena([trap])

    my_ball = MockBall(1, 100, 100, "teamA")
    ally = MockBall(2, 200, 200, "teamA")
    enemy = MockBall(3, 300, 300, "teamB")

    world = MockWorld(arena, [my_ball, ally, enemy])
    action = Action(my_ball, world)

    # Run a frame but block movement updates by nullifying vx/vy
    action.execute("none", 0.0) # Delta 0 stops movement processing from actually shifting position

    assert my_ball.x == 300
    assert my_ball.y == 300
    assert enemy.x == 100
    assert enemy.y == 100
    assert trap.duration == 0.0

def test_swap_trap_fallback():
    random.seed(42)
    trap = MockHazard("swap_trap")
    arena = MockArena([trap])

    my_ball = MockBall(1, 100, 100, "teamA")
    ally = MockBall(2, 200, 200, "teamA")

    world = MockWorld(arena, [my_ball, ally])
    action = Action(my_ball, world)

    action.execute("none", 0.0) # Delta 0

    assert my_ball.x == 200
    assert my_ball.y == 200
    assert ally.x == 100
    assert ally.y == 100
    assert trap.duration == 0.0
