import pytest
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.next_id = 99999
        self.mode = None
    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if getattr(b, "id", None) != getattr(ball, "id", None) and getattr(b, "team", "") != getattr(ball, "team", "")]}
    def _deal_damage(self, attacker, target):
        dmg = getattr(attacker, "damage", 10.0)
        target.take_damage(dmg)

class MockBall:
    def __init__(self, id=1):
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.team = "team1"
        self.ball_type = "normal"
        self.alive = True
        self.traits = []

    def take_damage(self, dmg):
        self.hp -= dmg

def test_laser_absorber_trait_absorbs_damage():
    world = MockWorld()

    attacker = MockBall(id=2)
    attacker.team = "team2"
    attacker.ball_type = "laser_beam"
    attacker.damage = 50.0

    target = MockBall(id=1)
    target.traits = ["laser_absorber"]
    target.hp = 100.0
    target.laser_energy_pool = 0.0

    action = Action(target, world)

    # Attempt damage from laser
    action._attempt_damage(attacker, target)

    # Should not take damage
    assert target.hp == 100.0
    # Should absorb energy
    assert target.laser_energy_pool == 50.0
    assert getattr(target, "laser_absorber_fire_ready", False) == False

    # Attack again to cross threshold
    action._attempt_damage(attacker, target)

    # Still no damage
    assert target.hp == 100.0
    # Energy pool resets and ready flag set
    assert getattr(target, "laser_energy_pool", 0.0) == 0.0
    assert getattr(target, "laser_absorber_fire_ready", False) == True

def test_laser_absorber_fire_laser():
    world = MockWorld()

    ball = MockBall(id=1)
    ball.x = 0.0
    ball.y = 0.0
    ball.team = "team1"
    ball.laser_absorber_fire_ready = True

    enemy = MockBall(id=2)
    enemy.x = 100.0
    enemy.y = 0.0
    enemy.team = "team2"
    world.balls.append(enemy)

    action = Action(ball, world)

    # Execute action
    action.execute("idle", 0.016)

    # Flag should reset
    assert ball.laser_absorber_fire_ready == False

    # New laser projectile should be added
    assert len(world.balls) == 2 # enemy + new laser
    laser = world.balls[-1]
    assert laser.ball_type == "projectile"
    assert laser.is_ricochet_laser == True
    assert laser.vx > 0 # Moving towards enemy (x=100)

    # Visual event added
    events = [e for e in world.events if e['type'] == 'visual_effect' and e['data']['type'] == 'focused_laser_fire']
    assert len(events) == 1
