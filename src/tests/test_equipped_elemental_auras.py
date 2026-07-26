import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.team = team
        self.alive = True
        self.ball_type = "player"
        self.base_speed = 100.0
        self.speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.equipped_aura = None
        self.level = 1

    def take_damage(self, dmg):
        self.hp -= dmg

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

def test_fire_aura():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "A")
    b2 = MockBall(2, 50, 0, "B")
    b1.equipped_aura = "fire"
    world.balls = [b1, b2]

    action = Action(b1, world)
    action.execute("idle", 1.0)

    assert b2.hp < 100.0  # Should take damage
    assert getattr(b2, "burn_timer", 0.0) > 0.0

def test_ice_aura():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "A")
    b2 = MockBall(2, 50, 0, "B")
    b1.equipped_aura = "ice"
    world.balls = [b1, b2]

    action = Action(b1, world)
    action.execute("idle", 1.0)

    assert getattr(b2, "freeze_timer", 0.0) > 0.0

def test_lightning_aura():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "A")
    b1.equipped_aura = "lightning"
    world.balls = [b1]

    action = Action(b1, world)
    action.execute("idle", 1.0)

    assert getattr(b1, "lightning_aura_active", False) == True
