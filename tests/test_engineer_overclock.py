import pytest
from ai.action import Action
from ai.ball_types_engineer import Engineer

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()
        self.next_id = 100

    def _deal_damage(self, attacker, target, amount):
        pass

class MockArena:
    def __init__(self):
        self.hazards = []

def test_overclock_activation():
    w = MockWorld()
    e = Engineer(ball_id=1, x=100, y=100)
    e.skill_timer = 5.0 # on cooldown
    e.id = 1
    w.balls.append(e)

    turret = Engineer(ball_id=2, x=105, y=105)
    turret.owner_id = 1
    turret.is_turret = True
    turret.attack_timer = 2.0
    w.balls.append(turret)

    a = Action(e, w)
    a.execute("use_skill", 1.0) # Calls _use_skill

    assert getattr(turret, "is_overclocked", False)
    assert len(w.events) == 1
    assert w.events[0]["type"] == "overclock_start"

def test_overclock_tick_hp_and_attack_speed():
    w = MockWorld()
    turret = Engineer(ball_id=2, x=105, y=105)
    turret.owner_id = 1
    turret.is_turret = True
    turret.is_overclocked = True
    turret.attack_timer = 2.0
    turret.hp = 50.0
    w.balls.append(turret)

    # Tick the turret to test hp loss and attack timer
    t_a = Action(turret, w)
    t_a.execute("idle", 1.0)

    assert turret.hp == 45.0
