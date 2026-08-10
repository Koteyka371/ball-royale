import pytest
from ai.action import Action
import random

class MockHazard:
    def __init__(self, kind="trap", trap_variant="time_dilation_mine"):
        self.kind = kind
        self.duration = 10.0
        self.x = 100
        self.y = 100
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1
        self.trap_variant = trap_variant
        self.owner_id = 999
        self.owner_team = "teamB"

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
        self.ball_type = "player"
        self.alive = True
        self.is_decoy = False
        self.radius = 10
        self.speed = 0
        self.base_speed = 0
        self.is_flying = False
        self.speed_debuff_timer = 0.0
        self.speed_debuff_multiplier = 1.0

def test_time_dilation_mine():
    random.seed(42)
    trap = MockHazard("trap", "time_dilation_mine")
    arena = MockArena([trap])

    my_ball = MockBall(1, 105, 105, "teamA")

    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.1)

    assert trap.duration == 0.0
    assert len(world.arena.hazards) == 2
    slow_zone = world.arena.hazards[-1]
    assert slow_zone.kind == "slow_zone"

    # Tick 2 to expand zone
    action.execute("none", 0.1)

    assert slow_zone.radius > 20.0
    assert my_ball.speed_debuff_timer == 8.0
    assert my_ball.speed_debuff_multiplier == 0.2
