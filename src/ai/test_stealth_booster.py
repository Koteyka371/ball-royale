from typing import Any
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.perception import Perception

class MockEntity:
    def __init__(self, x=0, y=0, kind="stealth_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
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
        self.stealth_booster_timer = 0.0
        self.speed = 2.0
        self.base_speed = 10.0
        self.stamina = 100.0
        self.max_hp = 100.0
        self.perception_radius = 250.0
        self.ball_type = "basic"
        self.shadow_booster_timer = 0.0

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


def test_stealth_booster_collection():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="stealth_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # timer set to 15.0, then decremented by 1.0 -> 14.0
    assert ball.stealth_booster_timer > 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_stealth_booster_perception():
    # If the ball has stealth_booster active, enemies shouldn't see it (or only see it from very close)
    spotter = MockBall(x=0, y=0)
    spotter.team = "spotter_team"

    target = MockBall(x=100, y=0)
    target.team = "enemy_team"
    target.stealth_booster_timer = 10.0 # stealth active

    world = MockWorld()
    world.balls = [spotter, target]

    p = Perception(spotter, world)
    # The method is get_perception_data in perception.py, wait, let's look at get_perception() or perceive()
    # It seems to be get_perception_data() based on standard Godot naming or get_data() ? Let's check perception.py
    state = p.scan()

    # target is 100 units away, stealth should hide it
    assert len(state["enemies"]) == 0

    target.x = 20 # very close, still shouldn't see it? Wait, stealth hides completely, or just up to a range?
    # Actually wait: e_has_stealth_booster: `if e_has_stealth_booster: continue` so it is COMPLETELY hidden from perception!
    state2 = p.scan()
    assert len(state2["enemies"]) == 0

    # Let's verify shadow_booster behavior as a baseline
    target.stealth_booster_timer = 0.0
    target.shadow_booster_timer = 10.0
    state3 = p.scan()
    assert len(state3["enemies"]) == 1 # 20 units away, shadow only hides > 30
