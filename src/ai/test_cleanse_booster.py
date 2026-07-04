from typing import Any
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, x=0, y=0, kind="cleanse_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
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
        self.immunity_timer = 0.0
        self.burn_timer = 5.0
        self.poison_timer = 5.0
        self.slow_timer = 5.0
        self.confusion_timer = 5.0
        self.is_confused = True
        self.blindness_timer = 5.0
        self.is_blinded = True
        self.zone_modifier_debuff = True
        self.base_max_hp = 150.0
        self.max_hp = 100.0

        self.speed = 2.0
        self.base_speed = 10.0
        self.stamina = 100.0
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


def test_cleanse_booster_collection():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="cleanse_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Ball immunity timer set to 15.0, decremented by 1.0 to 14.0
    assert ball.immunity_timer > 0.0
    assert ball.burn_timer == 0.0
    assert ball.poison_timer == 0.0
    assert ball.slow_timer == 0.0
    assert ball.confusion_timer == 0.0
    assert not ball.is_confused
    assert ball.blindness_timer == 0.0
    assert not ball.is_blinded
    assert not hasattr(ball, 'zone_modifier_debuff')
    assert ball.max_hp == ball.base_max_hp

    assert booster not in world.boosters
    assert booster not in world.arena.hazards
