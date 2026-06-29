import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.action import Action
from ai.ball_types_illusionist import Illusionist

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 999

def test_illusionist_deploy_static_decoy():
    world = MockWorld()
    ball = Illusionist(1, x=100.0, y=100.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # Pre-condition: only one ball
    assert len(world.balls) == 1

    # Execute the skill
    action.execute("use_skill", 0.1)

    # Post-condition: should have created a decoy
    assert len(world.balls) == 2

    decoy = world.balls[-1]

    # Check if the decoy has the expected attributes
    assert getattr(decoy, "is_decoy", False) is True
    assert getattr(decoy, "speed", -1) == 0.01  # Should be static (almost zero)
    assert getattr(decoy, "current_action", "") == "idle"
    assert decoy.id == 999
    assert decoy.damage == 0
