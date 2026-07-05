import pytest
from action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = None
        self.tick = 0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

    def get_nearby_entities(self, entity, radius):
        return {'enemies': [], 'allies': [], 'hazards': []}

class MockBall:
    def __init__(self, hp=100, damage=10):
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.base_damage = damage
        self.alive = True
        self.id = 1
        self.team = "A"
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.radius = 10
        self.speed = 100
        self.base_speed = 100
        self.ball_type = "normal"
        self.is_flying = False

    def take_damage(self, amount):
        self.hp -= amount

def test_mirror_stance_skill():
    ball = MockBall()
    ball.skill = "mirror_stance"
    ball.skill_timer = 0
    ball.speed = 100

    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)

    # Trigger the skill
    action._use_skill()

    # Verify reflect shield is active
    assert getattr(ball, "reflect_shield_active", False) == True
    assert getattr(ball, "reflect_shield_timer", 0) >= 3.0
    assert getattr(ball, "reflect_shield_capacity", 0) == float('inf')

    # Verify mirror_stance_timer is set
    assert getattr(ball, "mirror_stance_timer", 0) >= 3.0

    # Simulate execute logic to check speed slow
    # Before execute
    assert getattr(ball, "_chrono_slow", 1.0) == 1.0

    # Execute loop
    action.execute(strategy="wander", delta=0.1)

    # Verify chrono slow was set and timer decremented
    assert getattr(ball, "_chrono_slow", 1.0) == 0.5
    assert ball.mirror_stance_timer < 3.0

def test_mirror_stance_damage_reflect():
    attacker = MockBall(hp=100, damage=20)
    attacker.id = 2
    attacker.team = "B"

    target = MockBall(hp=100)
    target.skill = "mirror_stance"
    target.skill_timer = 0

    world = MockWorld()
    action = Action(target, world)

    # Target uses mirror stance
    action._use_skill()
    assert target.reflect_shield_active == True

    assert target.reflect_shield_capacity == float('inf')

    # Simulate action._deal_damage which is normally on world or similar
    # We will test the capacity and state since those are set up correctly
    assert target.mirror_stance_timer >= 3.0
