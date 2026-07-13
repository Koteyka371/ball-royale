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
        self.trap_variant = "ricochet"
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

def test_ricochet_trap_trigger():
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

    # Check if a ricochet laser was spawned
    lasers = [b for b in world.balls if getattr(b, "is_ricochet_laser", False)]
    assert len(lasers) == 1

    laser = lasers[0]
    assert laser.bounces_left == 5
    assert laser.damage == hazard.damage

def test_ricochet_laser_logic():
    owner = MockBall(id=2, x=200, y=200)
    enemy1 = MockBall(id=1, x=50, y=50)

    world = MockWorld()
    laser = type('MockBall', (), {})()
    laser.id = 999
    laser.ball_type = "projectile"
    laser.is_ricochet_laser = True
    laser.owner_id = owner.id
    laser.team = "player"
    laser.damage = 10.0
    laser.base_damage = 10.0
    laser.bounces_left = 5
    laser.last_hit_id = None
    laser.duration = 10.0
    laser.alive = True
    laser.x = 40
    laser.y = 40
    laser.vx = 100.0  # Moving towards enemy1 at 50,50
    laser.vy = 100.0
    laser.radius = 5.0

    world.balls = [enemy1, owner, laser]

    action = Action(laser.id, world)
    action.ball = laser

    # Tick 1: move towards enemy1 and hit
    action.execute("idle", 0.1) # x,y becomes 50,50, hits enemy1

    assert enemy1.hp == 90.0 # 100 - 10 damage
    assert getattr(enemy1, "slow_timer", 0.0) == 1.0
    assert laser.bounces_left == 4
    assert laser.last_hit_id == enemy1.id

    # Tick 2: hit again? Wait, it bounced off so it moves away. Let's force it to hit enemy1 again by reversing vx/vy
    laser.vx = -laser.vx
    laser.vy = -laser.vy
    laser.x = 45 # move back
    laser.y = 45

    action.execute("idle", 0.1) # hit enemy1 again
    assert enemy1.hp == 70.0 # 90 - 20 (double damage!)
    assert laser.bounces_left == 3
