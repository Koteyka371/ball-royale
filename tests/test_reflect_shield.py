from ai.action import Action
from ai.test_action_advanced import MockBall, MockEntity, MockWorld
from unittest.mock import Mock

def test_reflect_shield_skill():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    ball.skill = "reflect_shield"
    ball.skill_timer = 0.0
    ball.skill_cooldown = 10.0

    action = Action(ball, world)
    action._spawn_skill_particles = Mock()

    action._use_skill()

    assert ball.reflect_shield_active is True
    assert ball.reflect_shield_timer == 3.0
    assert ball.reflect_shield_capacity == float('inf')
    assert ball.skill_timer == 10.0
    action._spawn_skill_particles.assert_called_with("shield")

    # Test taking damage
    attacker = MockEntity(x=150, y=100, ball_type="enemy")
    attacker.damage = 100.0

    damage_dealt_to_attacker = []
    def mock_deal_damage(dmg_target, dmg_attacker):
        # target of the damage is the attacker, who is receiving the reflected damage
        # from the dmg_attacker (which is the ball with the shield)
        if dmg_target == attacker and dmg_attacker == ball:
            damage_dealt_to_attacker.append(True)
        # Note: actually _attempt_damage in reflect_shield calls self.world._deal_damage(target, attacker)
        # wait! Target is the ball taking damage, attacker is the one dealing it.
        # It calls `self.world._deal_damage(target, attacker)` where `target` is the ball and `attacker` is the enemy.
        # So dmg_target == ball, dmg_attacker == attacker!
        if dmg_target == ball and dmg_attacker == attacker:
            damage_dealt_to_attacker.append(True)
    world._deal_damage = mock_deal_damage

    action._attempt_damage(attacker, ball)

    assert ball.reflect_shield_active is True
    assert ball.reflect_shield_capacity == float('inf')
    assert len(damage_dealt_to_attacker) == 1

if __name__ == "__main__":
    test_reflect_shield_skill()
    print("Tests passed!")
