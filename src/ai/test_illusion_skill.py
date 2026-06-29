import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=50, y=50, team="red", ball_type="generic"):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.is_illusion = False
        self.illusion_timer = 0
        self.skill = "deploy_illusion"
        self.skill_timer = 0
        self.speed = 10
        self.damage = 10
        self.perception_radius = 200

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 100
    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

def test_deploy_illusion_taunt():
    world = MockWorld()
    caster = MockBall(50, 50, "red")
    illusion = MockBall(50, 50, "red")
    illusion.is_illusion = True
    illusion.hp = 1.0

    enemy = MockBall(100, 50, "blue")
    enemy.id = 2
    world.balls.extend([caster, illusion, enemy])

    action_enemy = Action(enemy, world)
    enemies = [caster, illusion]

    target = action_enemy._get_target(enemies)
    # Target should be illusion, not caster, because illusion taunts
    assert getattr(target, "is_illusion", False) == True

def test_illusion_explosion():
    world = MockWorld()
    illusion = MockBall(50, 50, "red")
    illusion.is_illusion = True
    illusion.hp = 1.0
    illusion.illusion_timer = 5.0

    enemy = MockBall(60, 50, "blue") # Near illusion
    world.balls.extend([illusion, enemy])

    # Simulate action loop to trigger global explosion check
    action = Action(illusion, world)

    # Kill the illusion
    illusion.hp = 0.0
    action.execute("idle", 0.1)

    assert illusion.alive == False
    assert getattr(illusion, "_illusion_exploded", False) == True

    # Enemy takes damage (20 from explosion)
    assert enemy.hp <= 100.0
