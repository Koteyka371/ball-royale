from ai.action import Action
from ai.test_action_advanced import MockBall, MockEntity, MockWorld
from unittest.mock import Mock

def test_reflect_shield_skill():
    ball = MockBall(x=100, y=100)
    ball.id = 2
    ball.alive = True
    ball.team = 1
    world = MockWorld()

    ball.skill = "reflect_shield"
    ball.skill_timer = 0.0
    ball.skill_cooldown = 10.0

    action = Action(ball, world)
    action._spawn_skill_particles = Mock()

    action._use_skill()

    assert ball.reflect_shield_active is True
    assert ball.reflect_shield_timer == 3.0
    assert ball.reflect_shield_capacity in [999999.0, 999899.0]
    assert ball.skill_timer == 10.0
    action._spawn_skill_particles.assert_called_with("shield")

    # Test taking damage
    attacker = MockEntity(x=150, y=100, ball_type="enemy")
    attacker.damage = 100.0
    attacker.id = 1
    attacker.alive = True
    attacker.team = 2

    damage_dealt_to_attacker = []
    def mock_deal_damage(dmg_target, dmg_attacker):
        if dmg_target == attacker and dmg_attacker == ball:
            damage_dealt_to_attacker.append(True)
    world._deal_damage = mock_deal_damage
    world.balls = [attacker, ball]

    action._attempt_damage(attacker, ball)

    assert ball.reflect_shield_active is True
    assert ball.reflect_shield_capacity in [999999.0, 999899.0]
    assert len(damage_dealt_to_attacker) == 1

if __name__ == "__main__":
    test_reflect_shield_skill()
    print("Tests passed!")
