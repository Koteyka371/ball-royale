import pytest
from unittest.mock import Mock
from ai.action import Action

class DummyBall:
    def __init__(self, x, y, team):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.hp = 100.0
        self.SKILL_COOLDOWN = 3.0
        self.skills = ["buff_drain"]
        self.active_skill = "buff_drain"
        self.skill = "buff_drain"
        self.skill_timer = 0.0
        self.silence_timer = 0.0
        self.intangible = False
        self.intangible_timer = 0.0
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.anchor_trap_timer = 0.0
        self.use_skill = lambda: None

class DummyWorld:
    def __init__(self):
        self.events = []
        self.balls = []

def test_buff_drain_with_buffs():
    world = DummyWorld()
    attacker = DummyBall(0, 0, 1)
    enemy = DummyBall(50, 50, 2)
    enemy.speed_boost_timer = 5.0
    enemy.insulator_timer = 3.0

    world.balls = [attacker, enemy]
    action = Action(attacker, world)

    action._get_enemies = lambda: [enemy]

    attacker.speed_boost_timer = 0.0
    attacker.insulator_timer = 0.0

    action._use_skill()

    assert enemy.speed_boost_timer == 0.0
    assert enemy.insulator_timer == 0.0
    assert attacker.speed_boost_timer == 5.0
    assert attacker.insulator_timer == 3.0
    assert enemy.hp == 100.0

def test_buff_drain_without_buffs():
    world = DummyWorld()
    attacker = DummyBall(0, 0, 1)
    enemy = DummyBall(50, 50, 2)

    world.balls = [attacker, enemy]
    action = Action(attacker, world)

    action._get_enemies = lambda: [enemy]

    action._use_skill()

    assert enemy.hp == 70.0
    assert any(e[0] == "damage_text" for e in world.events)
