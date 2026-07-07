import pytest
from ai.action import Action
import random

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.trap_variant = "normal"
        self.duration = 10.0
        self.x = 100
        self.y = 100
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1
        self.owner_id = 99

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
        self.boosters = []
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball and getattr(b, "team", "") != getattr(ball, "team", "")]}
    def _deal_damage(self, owner, target):
        pass

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
        self.hp = 100.0
        self.inventory = []

def test_mini_black_hole_trap():
    trap = MockHazard("trap")
    trap.trap_variant = "mini_black_hole"
    arena = MockArena([trap])

    my_ball = MockBall(1, 100, 100, "teamA")

    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.016)

    assert trap.duration == 0.0

    bh_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "mini_black_hole"]
    assert len(bh_hazards) == 1
    bh = bh_hazards[0]

    # Run another frame to see pulling
    # move my_ball away slightly to see it pulled back
    my_ball.x = 80
    my_ball.y = 80

    old_x, old_y = my_ball.x, my_ball.y
    action.execute("idle", 0.016)

    # Should move closer to 100, 100
    dist_old = ((old_x - 100)**2 + (old_y - 100)**2)**0.5
    dist_new = ((my_ball.x - 100)**2 + (my_ball.y - 100)**2)**0.5
    assert dist_new < dist_old

    # No damage
    assert my_ball.hp == 100.0
