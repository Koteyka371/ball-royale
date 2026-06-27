import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, ball_type="tank"):
        self.id = id_val
        self.ball_type = ball_type
        self.alive = True
        self.team = "None"

class MockWorld:
    def __init__(self):
        pass

def test_evolutionary_simulation_mode():
    mode = GAME_MODES["evolutionary_simulation"]
    balls = [MockBall(0, "tank"), MockBall(1, "tank"), MockBall(2, "spectator")]
    world = MockWorld()

    mode.setup(world, balls)

    assert balls[0].ball_type == "neural"
    assert balls[1].ball_type == "neural"
    assert balls[2].ball_type == "spectator"  # Spectator shouldn't be affected

    assert balls[0].team == "Neural_0"
    assert balls[1].team == "Neural_1"

    # Check draw condition
    balls[0].alive = False
    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Draw"

    # Check winning condition
    balls[0].alive = True
    assert mode.check_winner(world, balls) == "Neural_0"

    # Check no winner condition
    balls[1].alive = True
    assert mode.check_winner(world, balls) is None

test_evolutionary_simulation_mode()
print("Tests passed!")
