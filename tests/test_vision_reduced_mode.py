import pytest
import sys
import os

# Ensure src is in path to fix the import error from ai.interactive_training
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import VisionReducedMode

class MockBall:
    def __init__(self, ball_type="basic", alive=True):
        self.ball_type = ball_type
        self.alive = alive
        self.perception_radius = 250.0
        self.x = 500.0
        self.y = 500.0

def test_vision_reduced_mode_setup():
    mode = VisionReducedMode()
    class MockWorld:
        pass
    world = MockWorld()
    balls = [MockBall(), MockBall("spectator"), MockBall()]

    mode.setup(world, balls)

    assert balls[0].perception_radius == 50.0
    assert getattr(balls[0], "base_perception_radius", 250.0) == 250.0
    assert balls[0].team == "basic"

    assert balls[1].perception_radius == 250.0  # Spectator shouldn't be affected

    assert balls[2].perception_radius == 50.0

def test_vision_reduced_mode_tick():
    mode = VisionReducedMode()
    class MockWorld:
        pass
    world = MockWorld()
    balls = [MockBall()]
    mode.setup(world, balls)

    # Tick below 3.0s (no pulse)
    mode.tick(world, balls, 2.0)
    assert balls[0].perception_radius == 50.0

    # Tick above 3.0s (pulse active)
    mode.tick(world, balls, 1.1)
    assert mode.pulse_timer >= 3.0
    assert balls[0].perception_radius == 250.0 * 1.5

def test_vision_reduced_mode_check_winner():
    mode = VisionReducedMode()
    class MockWorld:
        pass
    world = MockWorld()
    balls = [MockBall(alive=True), MockBall(alive=False)]
    mode.setup(world, balls)

    winner = mode.check_winner(world, balls)
    assert winner == "basic"
