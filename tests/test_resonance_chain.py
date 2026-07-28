import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.arena = MockArena()
    def _deal_damage(self, attacker, target, dmg):
        if hasattr(target, "take_damage"):
            target.take_damage(dmg)
        else:
            target.hp -= dmg

class MockBall:
    def __init__(self, id, x, y, team="teamA"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.is_decoy = False
        self.owner_id = 1
        self.decoy_type = "explosive"
        self.decoy_timer = 5.0
        self._decoy_exploded = False
        self.vx = 0.0
        self.vy = 0.0
        self.stutter_timer = 0.0

def test_resonance_chain_explosion():
    # 3 decoys from same owner
    d1 = MockBall(2, 100, 100)
    d1.is_decoy = True
    d1.hp = 0  # Trigger explosion

    d2 = MockBall(3, 110, 110)
    d2.is_decoy = True
    d2.hp = 0

    d3 = MockBall(4, 90, 90)
    d3.is_decoy = True
    d3.hp = 0

    # 4th decoy not exploding yet
    d4 = MockBall(7, 400, 400)
    d4.is_decoy = True
    d4.hp = 100

    # Enemy within 400 radius (resonance chain range)
    enemy = MockBall(5, 120, 120, "teamB")

    # Far enemy
    far_enemy = MockBall(6, 600, 600, "teamB")

    world = MockWorld([d1, d2, d3, d4, enemy, far_enemy])
    action = Action(d1, world)
    action.execute("idle", 0.1)

    # All three decoys should be dead and marked as exploded
    assert d1._decoy_exploded is True
    assert d2._decoy_exploded is True
    assert d3._decoy_exploded is True
    assert d4._decoy_exploded is False

    # Enemy should take true damage (150) and have stutter timer
    assert enemy.hp == -50.0
    assert enemy.stutter_timer == 3.0

    # Far enemy should be unaffected
    assert far_enemy.hp == 100.0

    # Enemy should be pulled towards center (100, 100)
    assert enemy.vx < 0.0
    assert enemy.vy < 0.0

    # Check scorched earth hazard
    scorched_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "scorched_earth_zone"]
    assert len(scorched_hazards) == 1
    hazard = scorched_hazards[0]
    assert hazard.kind == "scorched_earth_zone"
    assert hazard.x == 100.0
    assert hazard.y == 100.0
    assert hazard.radius == 40.0
    assert hazard.damage == 5.0
    assert hazard.duration == 9999.0
    assert hazard.owner_id == 1

def test_no_resonance_chain_two_decoys():
    d1 = MockBall(2, 100, 100)
    d1.is_decoy = True
    d1.hp = 0

    d2 = MockBall(3, 110, 110)
    d2.is_decoy = True
    d2.hp = 0

    enemy = MockBall(5, 120, 120, "teamB")

    world = MockWorld([d1, d2, enemy])
    action = Action(d1, world)
    action.execute("idle", 0.1)

    assert d1._decoy_exploded is True
    assert d2._decoy_exploded is True

    # Regular double damage explosion = 60
    assert enemy.hp == 40.0

    # No scorched earth
    scorched_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "scorched_earth_zone"]
    assert len(scorched_hazards) == 0
