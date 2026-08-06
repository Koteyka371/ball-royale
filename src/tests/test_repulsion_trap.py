import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind, variant="repulsion"):
        self.kind = kind
        self.trap_variant = variant
        self.duration = 10.0
        self.x = 500
        self.y = 500
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1
        self.owner_id = 2

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        nx = max(radius, min(1000 - radius, x))
        ny = max(radius, min(1000 - radius, y))
        return (nx, ny, x != nx or y != ny)

class MockEventList(list):
    def append(self, event):
        super().append(event)

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0
        self.next_id = 9999
        self.delta = 0.1
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [], 'allies': []}

class MockBall:
    def __init__(self, id, x, y, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.radius = 10
        self.team = team
        self.inventory = []
        self.base_speed = 2.0
        self.speed = 2.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.cosmetic = "none"
        self.ball_type = "normal"
        self.is_frictionless = False

def test_repulsion_trap_trigger():
    trap = MockHazard("trap", variant="repulsion")
    arena = MockArena([trap])
    my_ball = MockBall(1, 500, 500)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.1)

    assert trap.duration == 0.0
    assert my_ball.is_frictionless == True
    assert my_ball.vx != 0.0 or my_ball.vy != 0.0
