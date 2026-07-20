import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=0, y=0):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10
        self.intangible = False
        self.intangible_timer = 0.0

class MockHazard:
    def __init__(self, owner_id):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "jump_pad"
        self.owner_id = owner_id
        self.x = 50
        self.y = 50
        self.radius = 15.0
        self.damage = 10.0
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
        self.events = []
    def _deal_damage(self, attacker, target, damage=None):
        dmg = damage if damage is not None else attacker.damage
        target.hp -= dmg
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_jump_pad_trap_trigger():
    owner = MockBall(id=2, x=200, y=200)
    triggering_ball = MockBall(id=1, x=45, y=45)

    world = MockWorld()
    hazard = MockHazard(owner_id=owner.id)
    world.arena.hazards.append(hazard)
    world.balls = [triggering_ball, owner]

    action = Action(triggering_ball.id, world)
    action.ball = triggering_ball

    action.execute("idle", 0.1)

    assert hazard.duration == 0.0

    # Ensure ball got knocked at high speed
    speed = math.sqrt(triggering_ball.vx**2 + triggering_ball.vy**2)
    assert speed > 290.0, f"Expected high speed, got {speed}"
