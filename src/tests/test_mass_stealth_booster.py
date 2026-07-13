import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.perception import Perception

class MockEntity:
    def __init__(self, x=0, y=0, kind="mass_stealth_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
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
        self.stealth_booster_timer = 0.0

    def get(self, key, default=None):
        return getattr(self, key, default)

    def has_method(self, name):
        return False

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=100.0, alive=True):
        super().__init__(x, y, "ball", radius, hp, alive)
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
            "allies": [b for b in self.balls if b.team == ball.team and b != ball],
            "boosters": self.boosters
        }

def test_mass_stealth_booster_collection():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    ally1 = MockBall(x=100, y=0) # within 200 units
    ally1.team = ball.team
    ally2 = MockBall(x=250, y=0) # outside 200 units
    ally2.team = ball.team

    booster = MockEntity(x=0, y=0, kind="mass_stealth_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.extend([ball, ally1, ally2])

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert ball.stealth_booster_timer > 0.0
    assert ally1.stealth_booster_timer > 0.0
    assert ally2.stealth_booster_timer == 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_mass_stealth_booster_perception_turret():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    turret = MockBall(x=105, y=100) # within 15 units (close)
    turret.team = "enemy"
    turret.is_turret = True

    # We are testing if the turret can see the ball
    ball.stealth_booster_timer = 5.0

    world.balls.append(ball)
    world.balls.append(turret)

    # Turret scans for enemies
    p = Perception(turret, world)
    data = p.scan()

    # The turret should completely ignore the stealthed enemy even if close
    assert len(data["enemies"]) == 0
