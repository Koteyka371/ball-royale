import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type('MockArena', (), {'hazards': []})()

    def _deal_damage(self, attacker, target):
        if hasattr(attacker, 'damage') and hasattr(target, 'hp'):
            target.hp -= attacker.damage

class MockBall:
    def __init__(self, id, x, y, team, max_hp=100.0, speed=100.0, damage=10.0, perception_radius=250.0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.max_hp = max_hp
        self.hp = max_hp
        self.speed = speed
        self.damage = damage
        self.perception_radius = perception_radius
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.intangible = False
        self.quantum_state_timer = 0.0
        self.ball_type = "player"

def test_juggernaut_stance():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "team1")
    target = MockBall(2, 5, 0, "team2")  # Close enough for melee

    import sys
    from unittest.mock import MagicMock, patch
    system_mock = MagicMock()
    lobby_mock = MagicMock()
    # The target will get the perks
    lobby_mock.get_perks.return_value = ["Thick Skinned", "Heavy Hitter"]
    system_mock.lobby.lobby = lobby_mock
    sys.modules["system"] = system_mock
    sys.modules["system.lobby"] = system_mock.lobby

    gm = GAME_MODES["battle_royale"]
    gm.apply_dynamic_traits = lambda w, b, d: None
    gm.setup(world, [target])

    assert getattr(target, "has_thick_skinned_perk", False)
    assert getattr(target, "has_heavy_hitter_perk", False)
    assert getattr(target, "has_juggernaut_stance", False)

    action = Action(attacker, world)

    with patch("random.random", return_value=0.0):
        # We need a control to compare the damage
        control_target = MockBall(3, 5, 0, "team2")

        # Test damage on target without Juggernaut
        action._attempt_damage(attacker, control_target)
        normal_damage = 100.0 - control_target.hp

        # Test damage on Juggernaut target
        action._attempt_damage(attacker, target)
        # Thick skinned increases max hp, so start max HP is 110
        juggernaut_damage = target.max_hp - target.hp

        assert juggernaut_damage == normal_damage * 0.7

if __name__ == "__main__":
    test_juggernaut_stance()
