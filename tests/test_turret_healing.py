import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def _deal_damage(self, attacker, target, dmg=None):
        pass

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.is_turret = False
        self.is_decoy = False

def test_turret_heals_allies():
    world = MockWorld()
    turret = MockBall(1, 0, 0, "red")
    turret.is_turret = True
    ally = MockBall(2, 50, 0, "red")
    ally.hp = 50.0
    enemy = MockBall(3, -50, 0, "blue")
    enemy.hp = 50.0
    world.balls = [turret, ally, enemy]

    action = Action(turret, world)
    action.execute("idle", 1.0)

    assert ally.hp == 55.0  # Healed by 5.0 * 1.0
    assert enemy.hp == 50.0 # No change
