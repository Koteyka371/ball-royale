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
    ball.id = 1
    world = MockWorld()

    booster = MockEntity(x=0, y=0, kind="stealth_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # timer set to 10.0, decremented by 1.0 -> 9.0
    assert ball.stealth_booster_timer > 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_stealth_booster_perception():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    enemy_ball = MockBall(x=120, y=100)
    enemy_ball.team = "enemy"
    enemy_ball.stealth_booster_timer = 5.0

    world.balls.append(ball)
    world.balls.append(enemy_ball)

    # distance is 20, stealth max distance is 15.0
    # enemy should not be seen
    p = Perception(ball, world)

    data = p.scan()
    assert len(data["enemies"]) == 0

    # distance is 10, should be seen
    enemy_ball.x = 110

    data = p.scan()
    assert len(data["enemies"]) == 1

def test_stealth_booster_ally_collection():
    ball = MockBall(x=0, y=0)
    ball.id = 1
    world = MockWorld()

    ally = MockBall(x=50, y=50)
    ally.id = 2
    ally.team = ball.team

    far_ally = MockBall(x=300, y=300)
    far_ally.id = 3
    far_ally.team = ball.team

    booster = MockEntity(x=0, y=0, kind="stealth_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)
    world.balls.extend([ball, ally, far_ally])

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Ball that collected it gets it
    assert ball.stealth_booster_timer > 0.0
    # Nearby ally gets it
    assert ally.stealth_booster_timer > 0.0
    # Far ally does not get it
    assert far_ally.stealth_booster_timer == 0.0

class MockTurret(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=50.0, alive=True):
        super().__init__(x, y, "turret", radius, hp, alive)
        self.is_turret = True
        self.owner_id = 123
        self.ball_type = "turret"
        self.team = "enemy"
        self.stealth_booster_timer = 0.0
        self.stealth_drone_timer = 0.0

def test_stealth_booster_hides_from_turret():
    turret = MockTurret(x=100, y=100)
    world = MockWorld()

    enemy_ball = MockBall(x=120, y=100)
    enemy_ball.team = "test_team" # Enemy of turret
    enemy_ball.stealth_booster_timer = 5.0
    enemy_ball.id = 555
    enemy_ball.alive = True

    ally_ball = MockBall(x=125, y=100)
    ally_ball.team = "test_team"
    ally_ball.stealth_booster_timer = 5.0
    ally_ball.id = 556
    ally_ball.alive = True

    world.balls.append(turret)
    world.balls.append(enemy_ball)
    world.balls.append(ally_ball)

    # Distance is 20 and 25. Max stealth distance is 15.
    p = Perception(turret, world)
    data = p.scan()
    assert len(data["enemies"]) == 0
