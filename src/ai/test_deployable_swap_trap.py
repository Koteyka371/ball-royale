import pytest
from ai.action import Action
import random

class MockHazard:
    def __init__(self, kind, x, y, duration=10.0, radius=200.0):
        self.kind = kind
        self.duration = duration
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = 0
        self.active = True
        self.id = 1
        self.activation_timer = 2.0
        self.owner_id = 1
        self.trap_triggered = False

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

def test_deployable_swap_trap_activates_and_swaps():
    trap = MockHazard("deployable_swap_trap", 100, 100, duration=10.0, radius=300.0)

    my_ball = MockBall(1, 100, 100, "teamA")  # Owner
    ally = MockBall(2, 200, 200, "teamA")     # 141.4 dist
    enemy = MockBall(3, 300, 300, "teamB")    # 282.8 dist (within 300)
    enemy2 = MockBall(4, 500, 500, "teamB")   # 565.6 dist (outside 300)

    world = MockWorld(MockArena([trap]), [my_ball, ally, enemy, enemy2])
    action = Action(my_ball, world)

    # Tick 1: Trap arms but timer > 0
    trap.activation_timer = 2.0
    action.execute("none", 1.0)
    assert trap.activation_timer == 1.0
    assert not getattr(trap, "trap_triggered", False)
    assert my_ball.x == 100 and my_ball.y == 100
    assert enemy.x == 300 and enemy.y == 300

    world.tick += 1
    # Tick 2: Trap triggers
    action.execute("none", 1.0)
    assert getattr(trap, "trap_triggered", True)
    assert trap.duration == 0.0 # Destroyed

    # Swap check - should swap owner and enemy
    assert my_ball.x == 300 and my_ball.y == 300
    assert enemy.x == 100 and enemy.y == 100
    assert ally.x == 200 and ally.y == 200     # Unaffected
    assert enemy2.x == 500 and enemy2.y == 500 # Unaffected
