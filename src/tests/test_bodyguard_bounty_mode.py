import pytest
from ai.game_modes import BodyguardBountyMode

class MockBall:
    def __init__(self, id_val, team_val, alive=True):
        self.id = id_val
        self.team = team_val
        self.alive = alive
        self.score = 0
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_damage = 10.0
        self.ball_type = "basic"
        self.x = 0
        self.y = 0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type_str, data):
        self.events.append({"type": type_str, "data": data})

def test_bodyguard_bounty_purchase_and_buff():
    mode = BodyguardBountyMode()
    world = MockWorld()

    b1 = MockBall(1, "TeamA")
    b2 = MockBall(2, "TeamA")

    b1.score = 100

    import random
    random.seed(42)  # Make random predictable if possible, though we might just bypass it or test over time

    # Tick many times to trigger the purchase chance
    # To avoid relying on random, we can force the purchase logic
    # Or just loop until it triggers.
    for _ in range(100):
        mode.tick(world, [b1, b2], delta=1.0)
        if b1.score < 100:
            break

    assert b1.score == 50
    assert 1 in mode.purchase_cooldowns
    assert 2 in mode.bounties

    # Target should be buffed
    assert getattr(b2, "is_bodyguard_bounty", False) == True
    assert getattr(b2, "high_threat", False) == True
    assert b2.max_hp == 150.0
    assert b2.hp == 150.0
    assert b2.base_damage == 15.0

    # Fast forward time to expire bounty
    for _ in range(21):
        mode.tick(world, [b1, b2], delta=1.0)

    assert 2 not in mode.bounties
    assert getattr(b2, "is_bodyguard_bounty", False) == False
    assert getattr(b2, "high_threat", False) == False
    assert b2.max_hp == 100.0
    assert b2.hp == 100.0
    assert b2.base_damage == 10.0

def test_bodyguard_bounty_claim():
    mode = BodyguardBountyMode()
    world = MockWorld()

    b1 = MockBall(1, "TeamA")
    b2 = MockBall(2, "TeamA")
    killer = MockBall(3, "TeamB")

    mode.bounties[2] = 20.0
    b2.is_bodyguard_bounty = True

    mode.on_ball_died(world, b2, killer)

    assert 2 not in mode.bounties
    assert killer.score == 100
