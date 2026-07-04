from typing import Any
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, x=0, y=0, kind="emp_immunity_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
        self.damage = damage
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.id = 999
        self.team = "test_team"
        self.ball_type = "booster"

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=100.0, alive=True):
        super().__init__(x, y, "ball", radius, hp, alive)
        self.emp_immunity_timer = 0.0
        self.is_emped = False
        self.is_scrambled = False
        self.has_drone = True
        self.has_shield = True
        self.speed_booster_timer = 10.0
        self.emp_timer = 0.0
        self.scramble_timer = 0.0
        self.speed = 2.0
        self.base_speed = 10.0
        self.stamina = 100.0
        self.max_hp = 100.0
        self.perception_radius = 250.0
        self.ball_type = "basic"

class MockArena:
    def __init__(self):
        self.hazards = []

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 1000

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }


def test_emp_immunity_booster_collection():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="emp_immunity_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # ball has timer set to 15.0, then decremented by 1.0 -> 14.0
    assert ball.emp_immunity_timer > 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_emp_immunity_blocks_emp_trap():
    ball = MockBall(x=100, y=100)
    ball.emp_immunity_timer = 5.0
    world = MockWorld()
    world.balls.append(ball)

    # Simulate emp_trap hazard damage logic inside execute
    trap = MockEntity(x=105, y=100, kind="trap")
    trap.trap_variant = "emp"
    trap.damage = 10.0
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Because ball has immunity, it shouldn't be emped
    assert not ball.is_emped
    assert ball.emp_timer == 0.0

def test_emp_immunity_blocks_emp_burst():
    ball = MockBall(x=100, y=100)
    ball.emp_immunity_timer = 5.0
    world = MockWorld()
    world.balls.append(ball)

    burst = MockEntity(x=105, y=100, kind="emp_burst")
    world.arena.hazards.append(burst)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert not ball.is_scrambled
    assert ball.scramble_timer == 0.0

def test_emp_immunity_blocks_emp_item():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    other_ball = MockBall(x=105, y=100)
    other_ball.team = "enemy_team"
    other_ball.emp_immunity_timer = 5.0

    world.balls.append(ball)
    world.balls.append(other_ball)

    # ball collects emp_item
    emp_item = MockEntity(x=100, y=100, kind="emp_item")
    world.boosters.append(emp_item)

    action = Action(ball, world)
    action.execute("collect_booster", 0.1)

    # other_ball should keep its drone and shield because it's immune
    assert other_ball.has_drone
    assert other_ball.has_shield
    assert other_ball.speed_booster_timer == 10.0
