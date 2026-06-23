import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from ai.ball_types_neural import Neural, NumpyArray

def test_neural_ball_creation_and_skill():
    ball = Neural(ball_id=99, x=50.0, y=50.0)
    assert ball.id == 99
    assert ball.BALL_TYPE == "neural"
    assert ball.hp == 100

    # Test numpy array operations
    a = NumpyArray([[1, 2], [3, 4]])
    b = NumpyArray([[5, 6], [7, 8]])
    c = a.matmul(b)
    assert c._data == [[19.0, 22.0], [43.0, 50.0]]

    # Test use skill changes action
    action_before = ball.current_action
    ball.use_skill()
    assert ball.current_action in ["attack", "flee", "idle", "defend"]
    assert ball.skill_timer == 4.0

test_neural_ball_creation_and_skill()
