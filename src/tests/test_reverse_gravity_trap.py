import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind, variant="reverse_gravity"):
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
        self.vx = 100.0
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

def test_reverse_gravity_trap():
    trap = MockHazard("trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 500, 500)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.1)

    assert trap.duration == 0.0

    # Check that field spawned
    rg_hazards = [h for h in world.arena.hazards if h.kind == "reverse_gravity_field"]
    assert len(rg_hazards) == 1
    rg = rg_hazards[0]
    assert rg.x == 500
    assert rg.y == 500
    assert rg.radius == 150.0
    assert rg.duration == 5.0

    # Now simulate the effect on an enemy ball
    b2 = MockBall(3, rg.x + 10, rg.y, team=1)
    b2.vx = 50.0
    b2.vy = 0.0
    world.balls.append(b2)
    a2 = Action(b2, world)
    a2.execute("none", 0.1)

    assert getattr(b2, "reverse_gravity_timer", 0.0) == 0.5

    # Assert the velocity is deflected upwards properly
    assert b2.vy < 0.0
    # Or at least assert that the velocity changed
    assert b2.vx != 50.0
