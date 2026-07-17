import math
class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "default"
        self.team = "team1"

class MockWorld:
    def __init__(self):
        self.events = []
        self.game_mode = None
        self.arena = lambda: None
        self.arena.hazards = []
        self.boosters = []

    def add_event(self, type, data):
        pass

def test_bounce_shield_melee():
    from ai.action import Action
    action = Action(MockBall(1, 0, 0), MockWorld())

    attacker = MockBall(2, 20, 20)
    target = MockBall(1, 0, 0)
    target.bounce_shield_active = True

    action._attempt_damage(attacker, target)
    assert attacker.hp == 90.0, "Attacker should take damage from melee reflection"
    assert target.hp == 100.0, "Target should not take damage"

def test_bounce_shield_ranged():
    from ai.action import Action
    action = Action(MockBall(1, 0, 0), MockWorld())

    attacker = MockBall(2, 100, 100)
    target = MockBall(1, 0, 0)
    target.bounce_shield_active = True

    action._attempt_damage(attacker, target)
    assert target.hp == 100.0, "Target should not take damage"
    assert hasattr(target, "suspended_projectiles"), "Target should have a suspended projectile"
    assert len(target.suspended_projectiles) == 1, "There should be one reflected projectile"
    assert target.suspended_projectiles[0]["target"] == attacker, "Reflected projectile target is the attacker"
    assert target.suspended_projectiles[0]["speed"] == 800.0, "Reflected projectile speed is 800"
