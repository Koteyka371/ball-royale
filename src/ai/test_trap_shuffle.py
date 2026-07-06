import pytest
from ai.action import Action
import random

class MockHazard:
    def __init__(self, kind, trap_variant="shuffle"):
        self.kind = kind
        self.trap_variant = trap_variant
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
        self.inventory = []
        self.active_skill = None

def test_shuffle_trap_swap():
    random.seed(42)
    trap = MockHazard("trap", trap_variant="shuffle")
    arena = MockArena([trap])

    my_ball = MockBall(1, 100, 100, "teamA")
    my_ball.inventory = ["itemA"]
    my_ball.active_skill = "skillA"

    target_ball = MockBall(2, 200, 200, "teamB")
    target_ball.inventory = ["itemB", "itemC"]
    target_ball.active_skill = "skillB"

    world = MockWorld(arena, [my_ball, target_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.0)

    # Assert trap destroyed
    assert trap.duration == 0.0

    # Assert timer and target id set
    assert getattr(my_ball, "shuffle_trap_timer", 0.0) == 10.0
    assert getattr(my_ball, "shuffle_target_id", None) == 2

    # Assert inventory and skills swapped
    assert my_ball.inventory == ["itemB", "itemC"]
    assert my_ball.active_skill == "skillB"
    assert target_ball.inventory == ["itemA"]
    assert target_ball.active_skill == "skillA"

def test_shuffle_trap_timer_expiration():
    arena = MockArena([])

    my_ball = MockBall(1, 100, 100, "teamA")
    # State while shuffled
    my_ball.inventory = ["itemB", "itemC"]
    my_ball.active_skill = "skillB"
    my_ball.shuffle_trap_timer = 0.1
    my_ball.shuffle_target_id = 2

    target_ball = MockBall(2, 200, 200, "teamB")
    target_ball.inventory = ["itemA"]
    target_ball.active_skill = "skillA"

    world = MockWorld(arena, [my_ball, target_ball])
    action = Action(my_ball, world)

    # Expire timer
    action.execute("none", 0.2)

    # Assert timer reset and target id cleared
    assert getattr(my_ball, "shuffle_trap_timer", -1.0) == 0.0
    assert getattr(my_ball, "shuffle_target_id", 1) is None

    # Assert inventory and skills swapped back
    assert my_ball.inventory == ["itemA"]
    assert my_ball.active_skill == "skillA"
    assert target_ball.inventory == ["itemB", "itemC"]
    assert target_ball.active_skill == "skillB"
