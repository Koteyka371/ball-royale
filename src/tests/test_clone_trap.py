import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.action import Action
from unittest.mock import MagicMock
import copy

class MockBall:
    def __init__(self, id=1, x=0, y=0, team="player"):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 100
        self.vy = 0
        self.team = team
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10

class MockHazard:
    def __init__(self, owner_id):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "clone"
        self.owner_id = owner_id
        self.x = 50
        self.y = 50
        self.radius = 15.0
        self.damage = 0.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 0
        self.next_id = 9999

def test_clone_trap_redirects_projectile():
    owner = MockBall(id=2, x=200, y=200, team="enemy")
    enemy = MockBall(id=3, x=50, y=200, team="player")
    triggering_projectile = MockBall(id=1, x=45, y=50, team="enemy") # Should clone if team != enemy
    triggering_projectile.ball_type = "projectile"

    world = MockWorld()
    hazard = MockHazard(owner_id=owner.id)
    world.arena.hazards.append(hazard)
    world.balls = [triggering_projectile, owner, enemy]

    action = Action(triggering_projectile.id, world)
    action.ball = triggering_projectile

    action.execute("idle", 0.1)

    assert hazard.duration == 0.0
    assert len(world.balls) == 4

    clone = world.balls[-1]
    assert clone.owner_id == hazard.owner_id
    assert clone.team == owner.team
