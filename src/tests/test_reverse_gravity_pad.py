import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind, variant="pad"):
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
        # A simple clamp for a 1000x1000 arena (0 to 1000)
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
        self.vx = 100.0  # moving right
        self.vy = 0.0
        self.alive = True
        self.radius = 10
        self.team = team
        self.inventory = []

def test_reverse_gravity_pad():
    pad = MockHazard("reverse_gravity_pad")
    pad.radius = 50.0
    arena = MockArena([pad])
    my_ball = MockBall(1, 500, 500)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    # Needs some variables for action.py
    my_ball.speed = 2.0
    my_ball.base_speed = 2.0
    my_ball.damage = 10.0
    my_ball.base_damage = 10.0
    my_ball.cosmetic = "none"
    my_ball.ball_type = "normal"

    action.execute("none", 0.1)

    assert getattr(my_ball, "reverse_gravity_item_timer", 0.0) == 3.0
