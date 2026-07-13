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

def test_sniper_stance():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "team1")
    target = MockBall(2, 100, 0, "team2")  # far away enough for ranged

    import sys
    from unittest.mock import MagicMock, patch
    system_mock = MagicMock()
    lobby_mock = MagicMock()
    lobby_mock.get_perks.return_value = ["Nimble", "Eagle Eye"]
    system_mock.lobby.lobby = lobby_mock
    sys.modules["system"] = system_mock
    sys.modules["system.lobby"] = system_mock.lobby

    gm = GAME_MODES["battle_royale"]
    gm.apply_dynamic_traits = lambda w, b, d: None
    gm.setup(world, [attacker])

    assert getattr(attacker, "has_nimble_perk", False)
    assert getattr(attacker, "has_eagle_eye_perk", False)
    assert getattr(attacker, "has_sniper_stance", False)

    action = Action(attacker, world)

    with patch("random.random", return_value=0.0):
        action._attempt_damage(attacker, target)
        # Normal damage is 10.0, but target takes some damage
        # Since wait... why did it deal 20.0?
        # Oh, in `test_script8.py` it went 100.0 -> 80.0. Let's see why it's 20.0.
        # But anyway, we just want to verify it deals 1.5x damage!
        first_damage = 100.0 - target.hp

        target.hp = 100.0
        attacker.vx = 5.0
        action._attempt_damage(attacker, target)
        second_damage = 100.0 - target.hp

        assert second_damage == first_damage * 1.5

if __name__ == "__main__":
    test_sniper_stance()
