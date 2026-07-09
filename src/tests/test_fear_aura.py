import pytest
from ai.action import Action

class MockBall:
    def __init__(self, i, x, y, team, level, aura):
        self.id = i
        self.x = x
        self.y = y
        self.team = team
        self.level = level
        self.cosmetic_aura_scale = aura
        self.alive = True
        self.emotion = "neutral"
        self.is_decoy = False

class MockWorld:
    def __init__(self):
        self.balls = []

def test_fear_aura_applied():
    world = MockWorld()
    # High-level ball with massive aura (scale >= 2.0)
    b1 = MockBall(1, 0, 0, "A", 5, 2.5)

    # Lower-level enemy ball nearby
    b2 = MockBall(2, 50, 0, "B", 1, 1.0)

    # Lower-level allied ball nearby (should not fear)
    b3 = MockBall(3, -50, 0, "A", 1, 1.0)

    # Higher-level enemy ball nearby (should not fear)
    b4 = MockBall(4, 0, 50, "B", 10, 1.0)

    # Distant lower-level enemy ball (should not fear)
    b5 = MockBall(5, 500, 500, "B", 1, 1.0)

    world.balls = [b1, b2, b3, b4, b5]

    action = Action(1, world)
    action.ball = b1

    # We use a large delta or mock random to guarantee the fear triggers.
    import random
    original_random = random.random
    random.random = lambda: 0.0 # Guarantee fear trigger

    action.execute("idle", 100.0)

    random.random = original_random

    assert b2.emotion == "fear", "Lower-level nearby enemy should be feared."
    assert b2.siren_feared_timer == 1.0

    assert b3.emotion == "neutral", "Allies should not be feared."
    assert b4.emotion == "neutral", "Higher-level enemies should not be feared."
    assert b5.emotion == "neutral", "Distant enemies should not be feared."

if __name__ == "__main__":
    test_fear_aura_applied()
    print("Test passed!")
