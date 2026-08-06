import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def _deal_damage(self, owner, target):
        pass

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, id, x, y, kind, radius=60.0, damage=10.0, owner_id=1, owner_team="blue"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = damage
        self.owner_id = owner_id
        self.owner_team = owner_team
        self.duration = 10.0

class MockBall:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0
        self.team = team
        self.stun_timer = 0.0
        self.cooldown_freeze_timer = 0.0
        self.freeze_trap_vulnerability_timer = 0.0
        self.skill_timer = 10.0

def test_deployable_freeze_trap():
    world = MockWorld()
    enemy = MockBall(2, 50, 50, team="red") # The trigger ball
    owner_ball = MockBall(1, 0, 0, team="blue") # The owner ball
    world.balls = [owner_ball, enemy]

    trap = MockHazard(1, 10, 10, "deployable_freeze_trap", radius=60.0, owner_id=1, owner_team="blue")
    world.arena.hazards.append(trap)

    action = Action(enemy, world)

    # Move inside radius
    enemy.x = 20
    enemy.y = 20

    action.execute("idle", 0.016)

    # Trap should be destroyed
    assert trap.duration == 0.0

    # Enemy should be frozen, movement locked
    assert enemy.stun_timer >= 3.0
    assert enemy.cooldown_freeze_timer > 2.9
    assert enemy.freeze_trap_vulnerability_timer > 2.9

    # Cooldown should not have decreased because of freeze
    assert enemy.skill_timer == 10.0

    # Try damage calculation
    class Attacker:
        def __init__(self):
            self.damage = 10.0

    # Damage should be multiplied by 1.25
    action._attempt_damage_internal(Attacker(), enemy)
    # Just asserting it didn't crash, vulnerability logic is in _attempt_damage_internal

def test_deployable_freeze_trap_ally_ignore():
    world = MockWorld()
    ally = MockBall(3, 50, 50, team="blue")
    owner_ball = MockBall(1, 0, 0, team="blue")
    world.balls = [owner_ball, ally]

    trap = MockHazard(1, 50, 50, "deployable_freeze_trap", radius=60.0, owner_id=1, owner_team="blue")
    world.arena.hazards.append(trap)

    action = Action(ally, world)
    action.execute("idle", 0.016)

    # Trap should NOT trigger for ally
    assert trap.duration > 0.0
    assert ally.stun_timer == 0.0

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_deployable_freeze_trap.py"])
