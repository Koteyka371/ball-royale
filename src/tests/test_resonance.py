import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team="red", is_decoy=False, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.is_decoy = is_decoy
        self.owner_id = owner_id
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.decoy_timer = 5.0
        self.radius = 10.0
        self.traits = []
        self.decoy_type = "explosive"

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.arena = MockArena()
        self.events = []
        self.next_id = 999

def test_resonance_chain():
    owner1 = MockBall(1, 0, 0, "red")
    owner2 = MockBall(2, 0, 0, "blue")

    # 3 decoys detonating simultaneously
    decoy1 = MockBall(3, 100, 100, "red", True, 1)
    decoy2 = MockBall(4, 110, 110, "red", True, 1)
    decoy3 = MockBall(5, 120, 120, "blue", True, 2)

    decoy1.hp = 0
    decoy2.hp = 0
    decoy3.hp = 0

    enemy1 = MockBall(6, 50, 50, "blue") # Initial hp is 100

    world = MockWorld([owner1, owner2, decoy1, decoy2, decoy3, enemy1])
    action = Action(owner1, world)
    action.execute("idle", 0.016)

    # Check for scorched earth hazard
    found_scorched = False
    for hazard in world.arena.hazards:
        if getattr(hazard, "kind", None) == "scorched_earth":
            found_scorched = True

    assert enemy1.hp < 0
    assert found_scorched

    # Check that pull occurred
    assert enemy1.x > 50
    assert enemy1.y > 50

    # Check visual effect
    found_vis = False
    for ev in world.events:
        if ev.get("type") == "visual_effect" and ev.get("data", {}).get("type") == "resonance_chain_explosion":
            found_vis = True
    assert found_vis
