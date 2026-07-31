import sys
from unittest.mock import MagicMock
sys.path.append('src')
from ai.action import Action

class MockBall:
    def __init__(self, hp=100, team="a"):
        self.id = 1
        self.hp = hp
        self.max_hp = 100
        self.x = 10
        self.y = 10
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.energy_shield_hp = 0.0
        self.energy_shield_active = False
        self.stun_timer = 0.0
        self.silence_timer = 0.0
        self.inventory = []
        self.use_item = False
        self.action = "idle"
        self.current_action = "idle"

class MockHazard:
    def __init__(self):
        self.kind = "deployable_lightning_rod"
        self.x = 0
        self.y = 0
        self.radius = 15.0
        self.team = "a"
        self.last_updated_tick = -1
        self.duration = 15.0
        self.pulse_radius = 250.0
        self.charge = 0.0
        self.max_charge = 100.0
        self.active = True
        self.damage = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.tick = 1
        self.balls = []
        self.events = []
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

    def _deal_damage(self, attacker, target, damage):
        target.hp -= damage

def test_deployable_lightning_rod_healing():
    world = MockWorld()

    hazard = MockHazard()

    ally = MockBall(50, "a")
    enemy = MockBall(100, "b")
    enemy.energy_shield_active = True
    enemy.energy_shield_hp = 50.0

    world.balls = [ally, enemy]
    world.arena.hazards = [hazard]

    action = Action(ally, world)

    action.execute("idle", 1.0)

    print(f"Ally shield: {ally.energy_shield_hp}")

    hazard.charge = 100.0
    hazard.last_updated_tick = 0
    world.tick = 2

    action.execute("idle", 1.0)

    print(f"Ally HP after heal: {ally.hp}")
    print(f"Enemy stun timer: {enemy.stun_timer}")
    print(f"Enemy shield HP: {enemy.energy_shield_hp}")

    assert ally.energy_shield_hp == 50.0, "Ally energy shield not set"
    assert ally.hp == 80.0, "Ally HP not healed"
    assert enemy.stun_timer == 0.0, "Enemy stun timer should be 0 (no longer stunning)"
    assert enemy.energy_shield_hp == 50.0, "Enemy energy shield should be untouched"
    print("Test passed")

test_deployable_lightning_rod_healing()
