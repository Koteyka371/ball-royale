import pytest
from ai.action import Action
from ai.test_action_advanced import MockWorld, MockBall

def test_deploy_decoy_flash_logic():
    ball = MockBall(x=10, y=10)
    ball.id = 111
    ball.team = "team_a"
    ball.skill = "deploy_decoy_flash"
    ball.skill_timer = 0.0

    world = MockWorld()
    world.balls = [ball]
    world.next_id = 222

    action = Action(ball, world)
    action._use_skill()

    assert len(world.balls) == 3
    decoy1 = world.balls[1]
    decoy2 = world.balls[2]

    assert decoy1.decoy_type == "flash"
    assert decoy2.decoy_type == "flash"

    # Add enemies
    enemy1 = MockBall(x=15, y=15)
    enemy1.team = "team_b"
    enemy1.id = 333
    enemy1.hp = 100
    enemy1.is_blinded = False

    enemy2 = MockBall(x=400, y=400) # Out of radius (300)
    enemy2.team = "team_b"
    enemy2.id = 444
    enemy2.hp = 100
    enemy2.is_blinded = False

    world.balls.extend([enemy1, enemy2])

    # Detonate decoy 1
    decoy1.hp = 0

    action.execute("idle", 0.1)

    assert getattr(decoy1, "_decoy_exploded", False) is True
    assert getattr(decoy2, "_decoy_exploded", False) is True

    # Enemy 1 should be blinded and take no damage
    assert enemy1.hp == 100
    assert getattr(enemy1, "is_blinded", False) is True
    assert getattr(enemy1, "blindness_timer", 0.0) == 3.0

    # Enemy 2 should not be blinded
    assert enemy2.hp == 100
    assert getattr(enemy2, "is_blinded", False) is False
