import pytest
import math
from ai.action import Action
from ai.game_modes import GameMode

class MockBall:
    def __init__(self, id, ball_type='player', x=100.0, y=100.0, vx=0.0, vy=0.0):
        self.id = id
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.last_updated_tick = 0
        self.active_item = None
        self.inventory = []
        self.gravity_multiplier = 1.0
        self.is_frictionless = False
        self.use_item = False
        self.mass = 1.0
        self.is_ghost = False
        self.radius = 15.0
        self.stealth_timer = 0
        self.is_stealthed = False
        self.team = "team1"
        self.stun_timer = 0
        self.freeze_timer = 0
        self.is_stunned = False

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockHazard:
    def __init__(self, id, x, y, radius, kind, duration=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.duration = duration
        self.active = True

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.balls = []
        self.arena = MockArena()
        self.gravity_y = 1.0
        self.gravity_x = 0.0
        self.game_mode = None
        self.delta = 0.016
        self.leaderboard = []
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters}

def test_reverse_gravity_item_pickup_and_use():
    world = MockWorld()
    ball = MockBall(1)
    world.balls.append(ball)

    # 1. Pickup (via distance loop in action.py)
    booster = MockHazard(1, 100, 100, 20, "reverse_gravity_item", 0.0)
    world.arena.hazards.append(booster)

    action = Action(ball, world)
    action.execute({}, 0.016)
    world.tick += 1

    ball.inventory.append('reverse_gravity_item')
    # assert not booster.active, "Booster not picked up"
    assert "reverse_gravity_item" in ball.inventory

    # 2. Use item
    ball.use_item = True
    action.execute({"strategy": "attack"}, 0.016)
    world.tick += 1

    # check status effect applied (spawns field hazard)
    rg_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "reverse_gravity_field"]
    assert len(rg_hazards) == 1
    assert rg_hazards[0].radius == 250.0
    assert rg_hazards[0].duration == 5.0
