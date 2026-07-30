import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockEntity:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.team = "A"
        self.skill = "spectral_burn"
        self.skill_timer = 0.0
        self.is_intangible = False
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_spectral_burn_skill():
    world = MockWorld()
    b1 = MockEntity(id=1, team="A")
    b2 = MockEntity(id=2, team="B", x=110.0, y=100.0) # Close enough for burn
    world.balls = [b1, b2]

    act = Action(b1, world)

    # Cast skill
    act._use_skill()

    assert getattr(b1, "spectral_burn_timer", 0.0) > 0.0
    assert getattr(b1, "intangible", False) == True

    # Tick
    b2_initial_hp = b2.hp
    act.execute("chase", 1.0)

    # Check if timer decreased and damage was dealt
    assert getattr(b1, "spectral_burn_timer", 0.0) == 2.0
    assert getattr(b1, "intangible", False) == True
    assert b2.hp < b2_initial_hp
    assert b2.hp == b2_initial_hp - 50.0

    # Wait for timer to expire
    act.execute("chase", 2.0)

    assert getattr(b1, "spectral_burn_timer", 0.0) == 0.0
    assert getattr(b1, "intangible", False) == False
