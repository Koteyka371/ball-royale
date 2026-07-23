import math
from ai.game_modes import GAME_MODES, ChainLightningMutatorMode

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.damage_dealt = []

    def add_event(self, type_str, data):
        self.events.append((type_str, data))

    def _deal_damage(self, attacker, target, damage):
        self.damage_dealt.append((attacker, target, damage))

class MockBall:
    def __init__(self, id_val, x, y, team):
        self.id = id_val
        self.x = x
        self.y = y
        self.team = team
        self.alive = True

def test_chain_lightning_mutator():
    mode = GAME_MODES.get("chain_lightning_mutator")
    assert mode is not None
    assert isinstance(mode, ChainLightningMutatorMode)

    # We want to force randomness to trigger chain lightning
    import random
    random.seed(42) # Should give predictable results

    # Hack the chance to 1.0 for testing
    mode.chain_chance = 1.0

    world = MockWorld()

    # Attackers and targets
    attacker_energy = type("EnergyWeapon", (), {"weapon_type": "energy", "team": "A"})()
    attacker_trap = type("Trap", (), {"kind": "some_trap", "team": "A"})()
    attacker_normal = type("Normal", (), {"team": "A"})()

    target = MockBall(1, 100, 100, team="B")

    # Other balls in range
    b1 = MockBall(2, 150, 100, team="B") # Distance 50 (in range)
    b2 = MockBall(3, 100, 200, team="C") # Distance 100 (in range, different team from A)
    b3 = MockBall(4, 500, 500, team="B") # Distance far (not in range)
    b4 = MockBall(5, 120, 100, team="A") # Same team as attacker (should not chain to team A)

    world.balls = [target, b1, b2, b3, b4]

    # 1. Normal damage (not energy/trap) -> no chain
    mode.on_damage_dealt(world, attacker_normal, target, 50.0)
    assert len(world.damage_dealt) == 0

    # 2. Energy damage -> chain
    mode.on_damage_dealt(world, attacker_energy, target, 50.0)
    assert len(world.damage_dealt) == 1
    att, targ, dmg = world.damage_dealt[0]
    assert att == attacker_energy
    assert targ in [b1, b2]
    assert dmg == 25.0
    assert any(e[0] == "chain_lightning" for e in world.events)

    world.damage_dealt.clear()
    world.events.clear()

    # 3. Trap damage -> chain
    mode.on_damage_dealt(world, attacker_trap, target, 40.0)
    assert len(world.damage_dealt) == 1
    att, targ, dmg = world.damage_dealt[0]
    assert att == attacker_trap
    assert targ in [b1, b2]
    assert dmg == 20.0
    assert any(e[0] == "chain_lightning" for e in world.events)
