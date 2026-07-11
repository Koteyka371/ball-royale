import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.team = "team"
        self.ball_type = "mock"
        self.is_decoy = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

def test_decoy_swap():
    world = MockWorld()

    decoy = MockBall(1, 100, 100)
    decoy.is_decoy = True
    decoy.decoy_type = "swap_trap"
    decoy.decoy_timer = 0  # Trigger explosion
    decoy.hp = 0

    p1 = MockBall(2, 110, 110)
    p2 = MockBall(3, 90, 90)

    world.balls = [decoy, p1, p2]

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    # They should have swapped positions or at least changed positions in some permutation
    # Since there are only 2 targets (p1, p2), they must have swapped exactly with each other
    # Or actually wait, the permutation shifts them.
    # first_pos = p1.orig
    # p1 gets p2.orig
    # p2 gets p1.orig
    assert (p1.x == 90 and p1.y == 90 and p2.x == 110 and p2.y == 110) or \
           (p1.x == 110 and p1.y == 110 and p2.x == 90 and p2.y == 90)

    assert decoy.alive == False
