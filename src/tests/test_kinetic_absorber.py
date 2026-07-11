import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []
        self.boosters = []
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball]}

class MockBall:
    def __init__(self, x, y, hp=100.0, team="red", ball_type="base", skill=None):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.team = team
        self.ball_type = ball_type
        self.skill = skill
        self.inventory = []
        self.radius = 10.0
        self.id = id(self)
        self.stamina = 100.0
        self.damage = 10.0
        self.speed = 100.0
        self.base_speed = 100.0

def test_kinetic_absorber_negates_knockback():
    world = MockWorld()
    b1 = MockBall(6, 5, team="red", skill="dash")
    b2 = MockBall(5, 5, team="blue", skill="kinetic_absorber")
    world.balls = [b1, b2]

    b1.is_dashing = True
    b2.inventory.append("kinetic_absorber_item")

    act = Action(b2, world)
    act._resolve_collisions()

    # Assert that b2 did not move (b2.x should be 5, not knocked back)
    assert math.isclose(b2.x, 5.0, abs_tol=0.1)
    assert getattr(b2, "kinetic_absorber_charge", 0.0) > 0.0
    assert getattr(b2, "speed_boost_timer", 0.0) > 0.0

def test_kinetic_absorber_explosion():
    world = MockWorld()
    b1 = MockBall(6, 5, team="red", skill="dash")
    b1.is_dashing = True
    b2 = MockBall(5, 5, team="blue", skill="kinetic_absorber")
    b2.kinetic_absorber_charge = 90.0
    b2.inventory.append("kinetic_absorber_item")
    world.balls = [b1, b2]

    act = Action(b2, world)
    act._resolve_collisions()

    assert b2.kinetic_absorber_charge == 0.0
    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'kinetic_explosion' for e in world.events)
    assert b1.hp < 100.0
    assert getattr(b1, "stun_timer", 0.0) == 1.5

if __name__ == "__main__":
    test_kinetic_absorber_negates_knockback()
    test_kinetic_absorber_explosion()
    print("Tests pass!")
