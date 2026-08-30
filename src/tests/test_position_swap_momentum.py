import pytest
from ai.game_modes import PositionSwapMode

class MockBall:
    def __init__(self, id, x, y, vx, vy, alive=True, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = alive
        self.team = team

class MockWorld:
    def __init__(self):
        self.position_swap_timer = 1.0
        self.position_swap_pending = False
        self.events = []
    def add_event(self, t, d):
        pass

def test_position_swap_momentum():
    world = MockWorld()
    ball_a = MockBall("A", 10.0, 20.0, 50.0, -10.0, team=1)
    ball_b = MockBall("B", 100.0, 200.0, -25.0, 75.0, team=2)
    balls = [ball_a, ball_b]
    mode = PositionSwapMode()

    # Trigger telegraph
    mode.apply_dynamic_traits(world, balls, 2.0)
    assert world.position_swap_pending

    # Trigger swap
    mode.apply_dynamic_traits(world, balls, 2.0)

    assert ball_a.x == 100.0
    assert ball_a.y == 200.0
    assert ball_a.vx == -25.0
    assert ball_a.vy == 75.0

    assert ball_b.x == 10.0
    assert ball_b.y == 20.0
    assert ball_b.vx == 50.0
    assert ball_b.vy == -10.0

if __name__ == "__main__":
    test_position_swap_momentum()
    print("Test passed.")
