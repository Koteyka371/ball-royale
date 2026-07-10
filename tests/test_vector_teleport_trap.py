import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.duration = 10.0
        self.x = 500
        self.y = 500
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
        nx = max(radius, min(x, self.width - radius))
        ny = max(radius, min(y, self.height - radius))
        return (nx, ny, False)

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
        return {'enemies': []}

class MockBall:
    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.team = "teamA"
        self.ball_type = "teamA"
        self.alive = True
        self.is_decoy = False
        self.radius = 10
        self.speed = 0
        self.base_speed = 0
        self.is_flying = False

def test_vector_teleport_trap_orthogonal():
    trap = MockHazard("vector_teleport_trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 500, 500, 100, 0)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.0)

    assert my_ball.x < 100
    assert trap.duration == 0.0

def test_vector_teleport_trap_diagonal():
    trap = MockHazard("vector_teleport_trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 500, 500, 100, 100)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.0)

    assert my_ball.x < 100
    assert my_ball.y < 100
    assert trap.duration == 0.0