import pytest
from unittest.mock import MagicMock
from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.ball_type = "ghost"
        self.skill = "ghost_walk"
        self.skill_timer = 0.0
        self.SKILL_COOLDOWN = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.alive = True
        self.team = "team1"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.traits = []
        self.vision_radius = 500.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.intangible_timer = 0.0
        self.hazard_immunity_timer = 0.0
        self.ghost_mode_active = False

def test_ghost_walk_skill():
    ball = MockBall()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.safe_zone_center = (500.0, 500.0)
    world.arena.safe_zone_radius = 500.0
    world.arena.clamp_position = MagicMock(return_value=(500.0, 500.0, False))
    action = Action(ball, world)

    # Trigger skill
    action._use_skill()

    assert ball.intangible == True
    assert ball.intangible_timer == 3.0
    assert ball.hazard_immunity_timer == 3.0
    assert ball.ghost_mode_active == True

def test_ghost_walk_damage_immunity():
    attacker = MockBall()
    target = MockBall()
    target.intangible = True
    target.intangible_timer = 3.0
    target.ghost_mode_active = True

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.safe_zone_center = (500.0, 500.0)
    world.arena.safe_zone_radius = 500.0
    world.arena.clamp_position = MagicMock(return_value=(500.0, 500.0, False))
    action = Action(attacker, world)

    # Try attacking
    # Attacking a target that has intangible and ghost_mode_active
    # In action.py: if target has ghost_mode_active, it dodges physical melee collisions
    # This just returns out of _attempt_damage
    # Let's set some dummy property to check if _attempt_damage continues
    target.take_damage = MagicMock()

    action._attempt_damage(attacker, target)
    target.take_damage.assert_not_called()

    # Check attacker attacking while intangible (should deal no damage)
    attacker.intangible = True
    target.intangible = False

    action._attempt_damage(attacker, target)
    target.take_damage.assert_not_called()

def test_ghost_walk_timer_decrement():
    ball = MockBall()
    ball.intangible = True
    ball.intangible_timer = 0.1
    ball.hazard_immunity_timer = 0.1
    ball.ghost_mode_active = True

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.safe_zone_center = (500.0, 500.0)
    world.arena.safe_zone_radius = 500.0
    world.arena.clamp_position = MagicMock(return_value=(500.0, 500.0, False))
    action = Action(ball, world)

    action.execute("idle", 0.2)

    assert ball.intangible == False
    assert ball.intangible_timer == 0.0
    assert ball.ghost_mode_active == False
