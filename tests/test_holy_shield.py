import pytest
from ai.action import Action

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
        self.ball_type = "paladin"
        self.is_flying = False

    def take_damage(self, amount):
        self.hp -= amount

def test_holy_shield_skill():
    ball = MockBall()
    ball.skill = "holy_shield"
    ball.skill_timer = 0
    ball.speed = 100

    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)

    # Trigger the skill
    action._use_skill()

    # Verify reflect shield is active
    assert getattr(ball, "reflect_shield_active", False) == True
    assert getattr(ball, "reflect_shield_timer", 0) >= 5.0
    assert getattr(ball, "reflect_shield_capacity", 0) == 100.0

def test_holy_shield_damage_reflect():
    attacker = MockBall(hp=100, damage=20)
    attacker.id = 2
    attacker.team = "B"
    attacker.ball_type = "warrior"

    target = MockBall(hp=100)
    target.skill = "holy_shield"
    target.skill_timer = 0

    world = MockWorld()
    action = Action(target, world)

    # Target uses holy shield
    action._use_skill()
    assert target.reflect_shield_active == True

    assert target.reflect_shield_capacity == 100.0

    # Test damage is partially absorbed
    # The shield logic in _attempt_damage reduces shield capacity

    action_attacker = Action(attacker, world)
    # Give world _deal_damage dummy method for testing
    def dummy_deal_damage(dmg_target, dmg_attacker):
        if hasattr(dmg_target, "take_damage"):
            dmg_target.take_damage(dmg_attacker.damage)
        elif hasattr(dmg_target, "hp"):
            dmg_target.hp -= dmg_attacker.damage

    world._deal_damage = dummy_deal_damage

    action_attacker._attempt_damage(attacker, target)

    # Original damage is 20. Target should reflect it back and shield capacity drops by 20.
    assert target.reflect_shield_capacity == 80.0
    assert target.reflect_shield_active == True
