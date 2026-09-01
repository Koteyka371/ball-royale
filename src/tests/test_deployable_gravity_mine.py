import pytest
from ai.action import Action
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []
        self.gravity_y = 500.0

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls or []
        self.arena = arena or MockArena()
        self.tick = 0
        self.events = []

class MockBall:
    def __init__(self, id):
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.vy = 0.0
        self.vx = 0.0
        self.alive = True
        self.is_frictionless = False
        self.inventory = []
        self.strategy = "attack"
        self.team = "A"
        self.hp = 100.0
        self.radius = 10.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.skill_timer = 0.0

class MockHazard:
    def __init__(self, id, x, y, kind="deployable_gravity_mine", radius=60.0, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.duration = 10.0
        self.owner_id = owner_id
        self.active = True

def test_deployable_gravity_mine_deployment_and_explosion():
    owner = MockBall(1)
    owner.x = 100.0
    owner.y = 100.0
    owner.inventory = ["deployable_gravity_mine"]

    enemy = MockBall(2)
    enemy.x = 110.0
    enemy.y = 100.0
    enemy.is_frictionless = False
    enemy.team = "B"

    world = MockWorld([owner, enemy])
    action_owner = Action(owner, world)

    action_owner.execute("attack", 0.1)

    assert "deployable_gravity_mine" not in owner.inventory
    assert len(world.arena.hazards) > 0
    mine = world.arena.hazards[0]
    assert mine.kind == "deployable_gravity_mine"
    assert mine.owner_id == owner.id

    action_enemy = Action(enemy, world)
    action_enemy.execute("attack", 0.1)

    assert mine.duration == 0.0
    assert getattr(owner, "gravity_swapped_timer", 0.0) == 5.0
    assert getattr(enemy, "gravity_swapped_timer", 0.0) == 5.0
    assert owner.is_frictionless == True
    assert enemy.is_frictionless == True

def test_deployable_gravity_mine_tick_effect():
    ball = MockBall(1)
    ball.vy = 50.0
    ball.gravity_swapped_timer = 5.0
    ball.was_frictionless = False
    ball.is_frictionless = True
    # Action might overwrite this in another place if some aura applies, let's just make it simple
    ball.strategy = "idle"

    world = MockWorld([ball])
    action = Action(ball, world)

    action.execute("idle", 0.1)

    assert ball.gravity_swapped_timer == 4.9
    assert ball.vy < 50.0 # Proves negative gravity force applied
    # is_frictionless isn't removed until timer reaches 0

    ball.gravity_swapped_timer = 0.05
    ball.is_frictionless = True # re-set just in case
    action.execute("idle", 0.1)
    assert ball.gravity_swapped_timer == 0.0
    assert ball.is_frictionless == False
