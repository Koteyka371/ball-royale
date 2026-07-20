from typing import Any
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.perception import Perception

class MockEntity:
    def __init__(self, x=0, y=0, kind="invisibility_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
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

    def has_method(self, name):
        return False

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=100.0, alive=True):
        super().__init__(x, y, "ball", radius, hp, alive)
        self.invisibility_timer = 0.0
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

def test_invisibility_booster_collection():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="invisibility_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # timer set to 10.0, decremented by 1.0 -> 9.0
    assert ball.invisibility_timer > 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_invisibility_booster_perception():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    enemy_ball = MockBall(x=120, y=100)
    enemy_ball.team = "enemy"
    enemy_ball.invisibility_timer = 5.0

    world.balls.append(ball)
    world.balls.append(enemy_ball)

    # Invisibility makes enemy completely invisible to AI
    p = Perception(ball, world)

    data = p.scan()
    assert len(data["enemies"]) == 0

    # Even right next to them
    enemy_ball.x = 101

    data = p.scan()
    assert len(data["enemies"]) == 0
