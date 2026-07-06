import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.alive = True
        self.speed_boost_timer = 0.0
        self.damage_multiplier = 1.0
        self.base_damage_multiplier = 1.0
        self.cursed_bumper_active = False
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.team = "A"
        self.state = "idle"
        self.cooldowns = {}
        self.active_skills = {}
        self.ball_type = "easy"
        self.perception_radius = 200.0
        self.used_skill_count = 0
        self.skill_timer = 0.0
        self.skill_cooldown = 0.0
        self.is_flying = False
        self.current_action = "none"
        self.is_exhausted = False
        self.is_dashing = False
        self._is_wind_riding = False
        self.infinite_stamina_timer = 0.0

class MockHazard:
    def __init__(self, x, y, kind="bumper", powerup_type=None):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 20.0
        self.kind = kind
        self.damage = 0.0
        self.powerup_type = powerup_type
        self.active = True
        self.duration = 10.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000.0
        self.height = 1000.0

    def update_zone(self, *args):
        pass

    def clamp_position(self, *args):
        return (0.0, 0.0, False)

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []
        self.events = []
        self.dead_balls = []

def test_cursed_bumper_activation_and_deactivation():
    ball = MockBall()
    ball.x = 10.0
    ball.y = 10.0
    ball.vx = 400.0 # Bumper doesn't explode

    cursed_bumper = MockHazard(10.0, 10.0, powerup_type="cursed")
    arena = MockArena([cursed_bumper])
    world = MockWorld(arena)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Hit cursed bumper
    action.execute("none", 0.1)

    assert ball.cursed_bumper_active is True
    assert ball.damage_multiplier == 2.0
    assert ball.speed_boost_timer > 0.0

    # Check DoT and stamina drain
    initial_hp = ball.hp
    initial_stamina = ball.stamina

    # Move away from bumper
    ball.x = 100.0
    ball.y = 100.0
    # Simulate movement so it doesn't count as "idle" and regenerate stamina
    ball.vx = 100.0
    action.execute("flee", 1.0)

    assert ball.hp < initial_hp
    assert math.isclose(ball.hp, initial_hp - 5.0)
    assert ball.stamina < initial_stamina

    # 2. Hit normal bumper
    ball.x = 100.0
    ball.y = 100.0
    normal_bumper = MockHazard(100.0, 100.0, powerup_type="heal")
    arena.hazards = [normal_bumper]

    action.execute("none", 0.1)

    assert ball.cursed_bumper_active is False
    assert ball.damage_multiplier == 1.0

def test_cursed_bumper_cleared_by_plain_bumper():
    ball = MockBall()
    ball.x = 10.0
    ball.y = 10.0
    ball.vx = 400.0 # Bumper doesn't explode

    cursed_bumper = MockHazard(10.0, 10.0, powerup_type="cursed")
    arena = MockArena([cursed_bumper])
    world = MockWorld(arena)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Hit cursed bumper
    action.execute("none", 0.1)

    assert ball.cursed_bumper_active is True

    # 2. Hit normal bumper
    ball.x = 100.0
    ball.y = 100.0
    normal_bumper = MockHazard(100.0, 100.0, powerup_type=None)
    arena.hazards = [normal_bumper]

    action.execute("none", 0.1)

    assert ball.cursed_bumper_active is False
    assert ball.damage_multiplier == 1.0
