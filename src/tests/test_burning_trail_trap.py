import sys
import os
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
        self.vx = 10.0
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
        self.speed_multiplier = 1.0
        self.slow_timer = 0.0

class MockHazard:
    def __init__(self, owner_id):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "burning_trail"
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

def test_burning_trail_trap_trigger():
    owner = MockBall(id=2, x=200, y=200)
    triggering_ball = MockBall(id=1, x=45, y=45)

    world = MockWorld()
    hazard = MockHazard(owner_id=owner.id)
    world.arena.hazards.append(hazard)
    world.balls = [triggering_ball, owner]

    action = Action(triggering_ball, world)

    action.execute("idle", 0.1)

    # Need a second tick because trap triggers at end of execute, but spawn is at beginning
    action.execute("idle", 0.1)

    # Trap should be destroyed
    assert hazard.duration == 0.0

    # Timer should be set
    assert triggering_ball.burning_trail_timer == 10.0

    # A trail puddle should be spawned since the ball was moving (vx=10.0)
    trail_puddles = [h for h in world.arena.hazards if getattr(h, "kind", "") == "burning_trail_puddle"]
    assert len(trail_puddles) == 1

    puddle = trail_puddles[0]
    assert puddle.duration == 2.0

def test_burning_trail_puddle_effect():
    enemy = MockBall(id=1, x=50, y=50)

    world = MockWorld()

    puddle = type('MockHazard', (), {})()
    puddle.id = 101
    puddle.kind = "burning_trail_puddle"
    puddle.x = 50
    puddle.y = 50
    puddle.radius = 20.0
    puddle.damage = 0.0
    puddle.duration = 2.0
    puddle.active = True
    puddle.owner_id = 2

    world.arena.hazards.append(puddle)
    world.balls = [enemy]

    action = Action(enemy, world)

    # Effect is applied passively in tick_hazards or similar
    action.execute("idle", 0.1)

    assert enemy.hp < 100.0
