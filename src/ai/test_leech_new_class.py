import sys
sys.path.insert(0, 'src')
from ai.action import Action
from ai.ball_types_leech import Leech
from unittest.mock import MagicMock

def test_leech_healing():
    world = MagicMock()
    attacker = Leech(1, 0, 0)
    attacker.hp = 50.0
    attacker.damage = 5.0
    target = MagicMock()
    target.id = 2
    target.x = 50
    target.y = 0
    target.hp = 100.0
    target.alive = True
    target.intangible = False
    target.intangible_timer = 0.0
    target.quantum_state_timer = 0.0
    target.invulnerable = False
    target.radius = 12.0
    world.balls = [attacker, target]
    action = Action(world, attacker)
    action._attempt_damage(attacker, target)
    assert attacker.hp == 60.0 # 50 + (5.0 * 2)
