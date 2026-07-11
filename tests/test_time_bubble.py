import pytest
import math

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.speed = 10.0
        self.base_speed = 100.0
        self.speed_multiplier = 1.0
        self.time_bubble_active = False
        self.ball_type = 'base'
        self.skill_timer = 10.0
        self.team = "blue"

class MockHazard:
    def __init__(self, kind):
        self.x = 0.0
        self.y = 0.0
        self.radius = 50.0
        self.kind = kind
        self.last_updated_tick = -1

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 1

    def get_nearby_entities(self, ball, radius):
        return {'boosters': [], 'hazards': self.arena.hazards, 'enemies': [], 'allies': []}

    def get_time(self):
        return 0.0

def test_time_bubble_execute():
    from ai.action import Action

    world = MockWorld()
    ball = MockBall()
    ball.x = 10.0
    ball.y = 10.0
    action = Action(ball, world)

    bubble = MockHazard("time_bubble")
    bubble.x = 10.0
    bubble.y = 10.0
    bubble.radius = 150.0
    world.arena.hazards.append(bubble)

    action.execute("idle", 1.0)

    # Verify time bubble properties
    assert ball.time_bubble_active == True

    # Speed and cooldowns
    assert math.isclose(ball.speed, 25.0, abs_tol=0.1) # 100.0 * 0.25
    assert math.isclose(ball.speed_multiplier, 0.25, abs_tol=0.1)

    # Expansion
    # original radius 150.0 + 10.0 * delta = 160.0
    assert math.isclose(bubble.radius, 160.0, abs_tol=0.1)
    assert bubble.last_updated_tick == 1

    # Skill cooldown reduced logic
    # Original skill_timer = 10.0. delta = 1.0, cooldown_mult = 0.25
    # 10.0 - 0.25 = 9.75
    assert math.isclose(ball.skill_timer, 9.75, abs_tol=0.1)


def test_time_bubble_projectile_suspension():
    from ai.action import Action

    world = MockWorld()
    attacker = MockBall()
    attacker.x = -100.0
    attacker.y = 0.0
    target = MockBall()
    target.x = 100.0
    target.y = 0.0
    target.team = "red"

    action = Action(attacker, world)

    bubble = MockHazard("time_bubble")
    bubble.x = 0.0
    bubble.y = 0.0
    bubble.radius = 50.0
    world.arena.hazards.append(bubble)

    action._attempt_damage(attacker, target)

    assert hasattr(attacker, "suspended_projectiles")
    assert len(attacker.suspended_projectiles) == 1

    proj = attacker.suspended_projectiles[0]
    assert proj["target"] == target
    assert math.isclose(proj["timer"], 4.0, abs_tol=0.1)
