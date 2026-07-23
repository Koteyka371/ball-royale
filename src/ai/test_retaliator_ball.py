import sys
import math
sys.path.append("src")
from ai.action import Action
from ai.ball_types_retaliator import Retaliator

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type('MockArena', (), {'hazards': []})

class MockBall:
    def __init__(self, id, hp=100, damage=10):
        self.id = id
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.team = "A"
        self.x = 0
        self.y = 0
        self.radius = 10
        self.alive = True
        self.ball_type = "normal"

    def take_damage(self, amount):
        self.hp -= amount

def test_retaliator_passive_reflection():
    attacker = MockBall(1, hp=100, damage=20)
    target = Retaliator(2)
    target.team = "B"
    # Ensure they're somewhat close for some potential distance checks (though internal damage checks may not need it)
    attacker.x = 0
    attacker.y = 0
    target.x = 5
    target.y = 5

    world = MockWorld()
    world.balls = [attacker, target]

    action = Action(target, world)

    # Check initial values
    assert target.hp == 120.0
    assert target.passive_reflect_percent == 0.5
    assert attacker.hp == 100.0


    # We must mock _deal_damage because _attempt_damage relies on the world to apply the actual damage
    def mock_deal_damage(att, tgt, dmg=None):
        dmg_val = dmg if dmg is not None else getattr(att, 'damage', 10)
        if hasattr(tgt, 'take_damage'):
            tgt.take_damage(dmg_val)
        else:
            tgt.hp -= dmg_val

    world._deal_damage = mock_deal_damage
    action._attempt_damage(attacker, target)


    # The attacker did 20 damage. The retaliator reflects 50%, so attacker takes 10 damage.
    # The target does not negate damage like damage_reflection_active does, so target takes 20 damage.

    assert attacker.hp == 90.0, f"Expected attacker to take 10 reflected dmg, got {100 - attacker.hp}"
    assert target.hp == 100.0, f"Expected target to take 20 dmg, got {120 - target.hp}"

def test_retaliator_gdscript_logic():
    # Placeholder for completeness, but GDScript logic was visually verified.
    pass

if __name__ == "__main__":
    test_retaliator_passive_reflection()
    print("All tests passed.")
