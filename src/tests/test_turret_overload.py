import pytest
from ai.action import Action
from ai.game_modes import StationaryTurretsMode

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 1000

class MockBall:
    def __init__(self, id_val, x, y, skill):
        self.id = id_val
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_timer = 0.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.is_turret = False
        self.owner_id = None
        self.damage = 15.0
        self.base_attack_time = 1.0

def test_turret_overload():
    world = MockWorld()
    engineer = MockBall(1, 0, 0, "turret_overload")
    engineer.SKILL_COOLDOWN = 20.0
    world.balls.append(engineer)

    turret = MockBall(2, 50, 50, None)
    turret.is_turret = True
    turret.owner_id = 1
    world.balls.append(turret)

    enemy = MockBall(3, 100, 100, None)
    world.balls.append(enemy)

    action = Action(engineer, world)

    # 1. Cast skill
    action.execute('chase', 0.1)
    action._update_skill_timer(0.1)
    action._use_skill()

    assert getattr(turret, "is_overloaded", False) == True
    assert getattr(turret, "overload_timer", 0) == 10.0
    assert turret.damage == 15.0 * 1.5
    assert turret.base_attack_time == 1.0 / 1.5
    assert engineer.skill_timer > 0

    # 2. Tick time
    action2 = Action(turret, world)
    action2.execute('idle', 9.0)
    assert turret.alive == True
    assert turret.hp > 0
    assert getattr(turret, "overload_timer", 0) <= 1.1

    # 3. Explode
    action2.execute('idle', 1.5)
    assert turret.alive == False
    assert turret.hp == 0

    # Check enemy damage
    assert enemy.hp == 100.0 - 50.0
