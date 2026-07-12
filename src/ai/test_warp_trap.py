import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.trap_variant = "warp"
        self.duration = 10.0
        self.x = 200
        self.y = 200
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
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [], 'allies': []}

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 100.0  # moving right
        self.vy = 0.0
        self.alive = True
        self.radius = 10

def test_warp_trap():
    trap = MockHazard("trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 200, 200)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    # execute, shouldn't move much except warp
    action.execute("none", 0.0)

    # Teleportation now random
    dist = math.hypot(my_ball.x - 200, my_ball.y - 200)
    assert dist <= 500.0 + 1e-5
    assert trap.duration == 0.0
    assert len(world.events) > 0
    assert world.events[-1]['type'] == 'teleport'
