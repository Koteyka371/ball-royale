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

def test_mimic_clone_movement():
    world = MockWorld()
    owner = MockBall(50, 50, "red")
    owner.id = 123
    owner.vx = 10.0
    owner.vy = -5.0

    clone = MockBall(50, 50, "red")
    clone.id = 124
    clone.is_mimic_clone = True
    clone.mimic_owner = 123
    clone.mimic_timer = 10.0
    clone.hp = 50.0

    world.balls.extend([owner, clone])

    action = Action(clone, world)
    action.execute("idle", 1.0)

    # Should copy velocity and move
    assert clone.vx == 10.0
    assert clone.vy == -5.0
    assert clone.x == 60.0
    assert clone.y == 45.0
    assert clone.mimic_timer == 9.0

def test_mimic_clone_does_not_explode():
    world = MockWorld()
    clone = MockBall(50, 50, "red")
    clone.is_mimic_clone = True
    clone.is_illusion = True
    clone.hp = 1.0
    clone.mimic_timer = 5.0
    clone.max_hp = 50.0

    enemy = MockBall(60, 50, "blue") # Near clone
    world.balls.extend([clone, enemy])

    action = Action(clone, world)

    # Trigger charge mode (kill the clone)
    clone.hp = 0.0
    action.execute("idle", 0.1)

    assert clone.alive == True # It heals and enters charge mode
    assert clone.is_mimic_clone == False
    assert clone.is_mimic_charging == True

    # Run it until it detonates
    # Do it in small steps because 4.0 delta in one step makes it jump too far!
    action.execute("idle", 0.1)
    action.execute("idle", 3.0)

    assert clone.alive == False
    # Enemy takes damage because it detonates
    assert enemy.hp == 80.0
