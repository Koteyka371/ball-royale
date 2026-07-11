import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.game_mode = None
        self.get_nearby_entities = lambda *args: []

class MockBall:
    def __init__(self, id, x, y, team, cosmetic):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.cosmetic = cosmetic
        self.radius = 10.0
        self.speed_boost_timer = 0.0

def test_kinetic_absorber():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, 1, "kinetic_absorber")
    b2 = MockBall(2, 5, 0, 2, "none")

    world.get_nearby_entities = lambda b, rad: {"enemies": [b2]} if b == b1 else {"enemies": [b1]}

    action = Action(b1, world)
    action._resolve_collisions()

    assert b1.x == 0.0, "x shouldn't change for b1 due to negated knockback"
    assert b1.speed_boost_timer > 0.0, "should get a speed boost"
    assert getattr(b1, "kinetic_absorbed_energy", 0.0) > 0.0, "should have absorbed energy"
