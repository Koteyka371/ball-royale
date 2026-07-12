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
    def __init__(self, id, x, y, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 100.0  # moving right
        self.vy = 0.0
        self.alive = True
        self.radius = 10
        self.team = team
        self.inventory = ["some_item"]

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
    b2 = MockBall(3, rg.x + 10, rg.y, team=1) # enemy ball (because owner_id is 2)
    b2.vx = 50.0
    b2.vy = 0.0
    world.balls.append(b2)
    a2 = Action(b2, world)
    a2.execute("none", 0.1)

    # Should push upwards and outwards
    assert b2.x > rg.x + 10
    assert b2.y < rg.y # Upwards is negative y
