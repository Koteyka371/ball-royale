import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
from ai.test_action_advanced import MockWorld, MockBall

def test_impostor_disguise():



    world = MockWorld()
    world.balls = []
    world.balls = []
    world.balls = []

    impostor = MockBall(x=50.0, y=50.0)
    impostor.id = 1
    impostor.team = "red"
    impostor.ball_type = "impostor"
    impostor.skill = "impostor_disguise"
    impostor.skill_timer = 0.0
    impostor.color = "gray"

    enemy = MockBall(x=60.0, y=50.0)
    enemy.id = 2
    enemy.team = "blue"
    enemy.color = "blue_color"
    enemy.hp = 100.0

    world.balls.extend([impostor, enemy])
    action = Action(impostor, world)

    # 1. Trigger the skill
    action._use_skill()

    assert getattr(impostor, "is_disguised", False) is True
    assert getattr(impostor, "disguise_timer", 0.0) == 5.0
    assert impostor.team == "blue"
    assert impostor.color == "blue_color"
    assert impostor.original_team == "red"
    assert impostor.original_color == "gray"

    # 2. Tick down disguise
    action.execute("idle", 4.0)

    assert getattr(impostor, "is_disguised", False) is True
    assert getattr(impostor, "disguise_timer", 0.0) == 1.0

    # 3. Timer expires, explosion happens
    action.execute("idle", 1.1)

    assert getattr(impostor, "is_disguised", False) is False
    assert impostor.team == "red"
    assert impostor.color == "gray"

    # Verify explosion damage on original enemies
    assert enemy.hp == 70.0 # took 30 damage

    print("test_impostor_disguise passed")

if __name__ == "__main__":
    test_impostor_disguise()
