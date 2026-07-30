import pytest
from ai.game_modes import PermutationSwapMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick_count = 0
        self.events = []
        self.next_id = 10

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 25.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "team"
        self.ball_type = "mock"

def test_permutation_swap_mode():
    mode = PermutationSwapMode()
    world = MockWorld()

    b1 = MockBall(1, 500.0, 500.0) # In center
    b2 = MockBall(2, 510.0, 500.0) # Close to center
    b3 = MockBall(3, 100.0, 100.0) # Outside the zone

    world.balls = [b1, b2, b3]

    mode.setup(world, world.balls)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "permutation_swap_zone"
    assert hazard.x == 500.0
    assert hazard.y == 500.0
    assert hazard.radius == 200.0

    # Store initial positions for comparison
    b1_initial = (b1.x, b1.y)
    b2_initial = (b2.x, b2.y)
    b3_initial = (b3.x, b3.y)

    # Timer starts at 3.0
    for _ in range(29): # 2.9 seconds
        mode.tick(world, world.balls, 0.1)

    assert hazard.swap_timer > 0.0

    mode.tick(world, world.balls, 0.1) # Trigger the swap

    # b3 should NOT move
    assert (b3.x, b3.y) == b3_initial

    # b1 and b2 should have swapped
    assert (b1.x, b1.y) == b2_initial or (b1.x, b1.y) == b1_initial
    assert (b2.x, b2.y) == b1_initial or (b2.x, b2.y) == b2_initial

    # Since there are only 2 targets, they must have swapped exactly with each other
    assert (b1.x, b1.y) == b2_initial
    assert (b2.x, b2.y) == b1_initial

    # Timer should have reset
    assert hazard.swap_timer == 3.0
