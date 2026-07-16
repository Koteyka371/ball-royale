import pytest
from ai.action import Action
from ai.test_action_advanced import MockWorld, MockBall

def test_shuffler_clone_spawns():
    world = MockWorld()
    ball = MockBall(x=100, y=100)
    ball.ball_type = "shuffler"
    ball.team = "blue"
    ball.vx = 5.0
    ball.vy = 0.0
    ball.shuffler_clone_timer = 0.1
    world.balls = [ball]

    action = Action(ball, world)
    action.execute("idle", 0.2)

    # Clone should have spawned
    assert len(world.balls) == 2
    clone = world.balls[1]
    assert getattr(clone, "is_shuffler_clone", False) == True
    assert clone.max_hp == 1.0
    assert clone.damage == 0.0
    assert clone.vx == 5.0

def test_shuffler_clone_blinds_attacker():
    world = MockWorld()
    target = MockBall(x=100, y=100)
    target.is_shuffler_clone = True
    target.team = "blue"

    attacker = MockBall(x=100, y=100)
    attacker.team = "enemy"

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert getattr(attacker, "is_blinded", False) == True
    assert getattr(attacker, "blindness_timer", 0.0) >= 3.0
