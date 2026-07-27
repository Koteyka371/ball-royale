import pytest
from ai.echolocation_only import EcholocationOnlyMode

class MockBall:
    def __init__(self, alive=True, ball_type="normal", perception_radius=200.0):
        self.alive = alive
        self.ball_type = ball_type
        self.perception_radius = perception_radius

class MockWorld:
    def __init__(self):
        pass

def test_echolocation_only_mode():
    mode = EcholocationOnlyMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall(alive=False)
    b3 = MockBall(ball_type="spectator")

    balls = [b1, b2, b3]

    # Test setup
    mode.setup(world, balls)

    assert b1.perception_radius == 50.0
    assert b1.base_perception_radius == 200.0

    # Spectator should not be affected
    assert b3.perception_radius == 200.0

    # Test tick - before pulse
    mode.tick(world, balls, delta=2.0)
    assert b1.perception_radius == 50.0

    # Test tick - during pulse
    mode.tick(world, balls, delta=1.5)
    # Total timer is 3.5. > 3.0 (pulse_interval) so it should be pulsing
    assert b1.perception_radius == 1000.0

    # Test tick - after pulse reset
    mode.tick(world, balls, delta=1.0)
    # Total timer is 4.5. > 3.5 (pulse_interval + duration) so it resets to 1.0. (1.0 <= 3.0) -> not pulsing
    assert b1.perception_radius == 50.0
