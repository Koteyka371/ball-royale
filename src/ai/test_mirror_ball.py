import pytest
from ai.ball_types_mirror import Mirror
from ai.action import Action
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, id=1, team="enemy"):
        self.id = id
        self.team = team
        self.x = 10
        self.y = 10
        self.alive = True
        self.ball_type = "enemy"
        self.poison_timer = 0.0
        self.emp_timer = 0.0
        self.is_emped = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MagicMock()
        self.arena.safe_zone_center = (0, 0)
        self.arena.safe_zone_radius = 500
        self.arena.clamp_position = MagicMock(return_value=(0, 0, False))

def test_mirror_ball_kinetic_vulnerability():
    mirror = Mirror(1)
    mirror.hp = 170
    mirror.max_hp = 170

    # 2.0x kinetic multiplier, so taking 10 should deal 20
    mirror.take_damage(10)
    assert mirror.hp == 130

def test_mirror_ball_reflects_statuses():
    mirror = Mirror(1)
    mirror.ball_type = "mirror"
    mirror.team = "mirror"
    mirror.x = 0
    mirror.y = 0

    enemy = MockBall(2, "enemy")

    world = MockWorld()
    world.balls = [mirror, enemy]

    # Apply negative statuses to mirror
    mirror.poison_timer = 5.0
    mirror.emp_timer = 3.0
    mirror.is_emped = True

    # Mock some required attrs for Action init / execution
    mirror.max_stamina = 100
    mirror.stamina = 100
    mirror.base_speed = 2.5
    mirror.speed = 2.5
    mirror.base_damage = 16
    mirror.original_base_damage = 16
    mirror.traits = []
    mirror.weather_immunity_timer = 0
    mirror.in_mirror_dimension = False
    mirror.intangible = False
    mirror.vision_radius = 230
    mirror.invisible = False
    mirror.speed_multiplier = 1.0
    mirror.hp = 170
    mirror.max_hp = 170
    mirror.id = 1
    mirror.alive = True

    enemy.max_stamina = 100
    enemy.stamina = 100
    enemy.base_speed = 2.5
    enemy.speed = 2.5
    enemy.base_damage = 16
    enemy.original_base_damage = 16
    enemy.traits = []
    enemy.weather_immunity_timer = 0
    enemy.in_mirror_dimension = False
    enemy.intangible = False
    enemy.vision_radius = 230
    enemy.invisible = False
    enemy.speed_multiplier = 1.0
    enemy.hp = 170
    enemy.max_hp = 170

    action = Action(mirror, world)
    action.execute("idle", 0.016)

    assert enemy.poison_timer == 5.0
    assert enemy.emp_timer == 3.0
    assert enemy.is_emped == True

    assert mirror.poison_timer == 0.0
    assert mirror.emp_timer == 0.0
    assert mirror.is_emped == False
