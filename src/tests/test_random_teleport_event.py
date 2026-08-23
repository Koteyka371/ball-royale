import pytest
from ai.game_modes import GAME_MODES

def test_random_teleport_event():
    # Setup mock world and balls
    class MockWorld:
        def __init__(self):
            self.events = []

        def add_event(self, event_type, data):
            self.events.append((event_type, data))

    class MockBall:
        def __init__(self, id, x, y, team):
            self.id = id
            self.x = x
            self.y = y
            self.team = team
            self.alive = True
            self.ball_type = "player"

    world = MockWorld()
    b1 = MockBall("b1", 10.0, 10.0, "Team A")
    b2 = MockBall("b2", 100.0, 100.0, "Team B")
    balls = [b1, b2]

    # Find RandomTeleportEventMode in GAME_MODES
    mode = GAME_MODES.get('random_teleport_event')
    assert mode is not None, "Mode should be registered in GAME_MODES"

    # Setup the mode
    mode.setup(world, balls)

    # Fast forward trigger timer
    mode.trigger_timer = 0.001

    # Tick to trigger the warning event and setup the swap
    mode.tick(world, balls, delta=0.016)

    assert mode.active_swap is not None
    assert len(world.events) == 1
    assert world.events[0][0] == "teleport_swap_warning"

    # Get the balls involved in the swap
    swap_b1, swap_b2 = mode.active_swap['balls']
    assert set([swap_b1.id, swap_b2.id]) == set(["b1", "b2"])

    # Fast forward the swap timer
    mode.active_swap['timer'] = 0.001

    # Remember original positions
    orig_b1_pos = (b1.x, b1.y)
    orig_b2_pos = (b2.x, b2.y)

    # Tick to execute swap
    mode.tick(world, balls, delta=0.016)

    # Ensure active swap is cleared
    assert mode.active_swap is None

    # Ensure positions were swapped
    assert b1.x == orig_b2_pos[0]
    assert b1.y == orig_b2_pos[1]
    assert b2.x == orig_b1_pos[0]
    assert b2.y == orig_b1_pos[1]

    # Ensure event was added
    assert len(world.events) == 2
    assert world.events[1][0] == "teleport_swap_complete"
