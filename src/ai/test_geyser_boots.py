import sys
import os
import math
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id=1, ball_type="normal", hp=100.0, x=0.0, y=0.0):
        self.id = id
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = 100.0
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed_buff_timer = 0.0
        self.geyser_immunity_timer = 0.0
        self.stun_timer = 0.0
        self.base_speed = 10.0
        self.speed = 10.0
        self.alive = True
        self.inventory = []
        self.intangible = False
        self.intangible_timer = 0.0
        self.terminal_velocity = 99999.0

class MockBooster:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.time = 0.0
        self.tick = 0
    def _deal_damage(self, attacker, target, dmg=0.0):
        target.hp -= dmg

def test_geyser_boots_collection():
    ball = MockBall(x=10.0, y=10.0)
    booster = MockBooster(1, 10.0, 10.0, "geyser_boots")
    world = MockWorld()
    world.balls.append(ball)
    world.boosters.append(booster)
    world.arena.hazards.append(booster)

    action = Action(ball, world)

    action._collect_booster(1.0)

    assert "geyser_boots" in ball.inventory
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_geyser_boots_immunity_and_launch():
    world = MockWorld()
    world.time = 1.0 # Erupting window

    ball = MockBall(x=0.0, y=0.0)
    ball.inventory.append("geyser_boots")
    world.balls.append(ball)

    geyser = Hazard(1, 0.0, 0.0, 50.0, "geyser", 10.0)
    world.arena.hazards.append(geyser)

    action = Action(ball, world)

    # We use a very small delta so the speed decay does not mask the launch force
    action.execute("idle", 0.0)

    # Check immunity to damage and stun
    assert ball.hp == 100.0
    assert ball.stun_timer == 0.0

    # Check immunity timer is applied
    assert ball.geyser_immunity_timer == 3.0

    # Check enhanced launch force
    speed = math.hypot(ball.vx, ball.vy)
    assert abs(speed - 3500.0) < 1.0

def test_geyser_boots_normal_behavior_without_boots():
    world = MockWorld()
    world.time = 1.0 # Erupting window

    ball = MockBall(x=0.0, y=0.0)
    world.balls.append(ball)

    geyser = Hazard(1, 0.0, 0.0, 50.0, "geyser", 10.0)
    world.arena.hazards.append(geyser)

    action = Action(ball, world)
    action.execute("idle", 0.0)

    # Check damage and stun applied
    assert ball.hp < 100.0
    assert ball.stun_timer > 0.0

    # Check normal launch force
    speed = math.hypot(ball.vx, ball.vy)
    assert abs(speed - 1500.0) < 1.0
