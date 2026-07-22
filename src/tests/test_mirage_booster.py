from typing import Any
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, x=0, y=0, kind="mirage_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
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
        self.speed = 2.0
        self.base_speed = 10.0
        self.stamina = 100.0
        self.max_hp = 100.0
        self.perception_radius = 250.0
        self.ball_type = "basic"
        self.mirage_booster_timer = 0.0

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

def test_mirage_booster_collection_and_tick():
    ball = MockBall(x=0, y=0)
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="mirage_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert ball.mirage_booster_timer == 15.0
    assert hasattr(ball, "mirage_spawn_timer")

    # Tick execution 3 times by 1.0 delta to spawn
    action.execute("flee", 1.0)
    action.execute("flee", 1.0)
    action.execute("flee", 1.0)

    assert ball.mirage_booster_timer == 12.0
    assert ball.mirage_spawn_timer == 0.0

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "mirage_decoy"
    assert world.arena.hazards[0].owner_id == ball.id

    decoy = world.arena.hazards[0]

    # Spawn enemy near decoy
    enemy_ball = MockBall(x=10, y=10)
    enemy_ball.id = 1001
    enemy_ball.team = "enemy"
    world.balls.append(enemy_ball)

    action.execute("flee", 0.1) # Check collision

    has_emp = False
    for h in world.arena.hazards:
        if getattr(h, "kind", "") == "emp_burst":
            has_emp = True
            assert getattr(h, "damage", 0.0) == 20.0
    assert has_emp, "EMP burst was not created"
