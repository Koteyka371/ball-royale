import pytest
import math
from ai.game_modes import GameMode

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.gold = 0
        self.max_hp = 100
        self.hp = 100
        self.base_speed = 100
        self.speed = 100
        self.base_damage = 10
        self.damage = 10

def test_gold_earned_on_kill():
    world = MockWorld()
    mode = GameMode()
    killer = MockBall("killer", 0, 0)
    victim = MockBall("victim", 0, 0)

    # Assert initial gold
    assert killer.gold == 0

    # Simulate death
    mode.on_ball_died(world, victim, killer)

    # Assert gold earned
    assert killer.gold == 50
    assert any(e[0] == "gold_earned" for e in world.events)

def test_shop_upgrade_tick():
    world = MockWorld()
    mode = GameMode()

    # Place one ball directly in the shop with enough gold, and another far away
    buyer = MockBall("buyer", 500.0, 500.0)
    buyer.gold = 100

    non_buyer = MockBall("non_buyer", 0.0, 0.0)
    non_buyer.gold = 100

    balls = [buyer, non_buyer]

    mode.tick(world, balls, delta=0.016)

    # Buyer should have spent gold and gotten an upgrade
    assert buyer.gold == 0
    assert any(e[0] == "shop_upgrade" for e in world.events)
    assert (buyer.max_hp == 120 or buyer.base_speed == 115 or buyer.base_damage == 15)

    # Non-buyer should keep their gold and not get an upgrade
    assert non_buyer.gold == 100
    assert non_buyer.max_hp == 100
    assert non_buyer.base_speed == 100
    assert non_buyer.base_damage == 10

if __name__ == "__main__":
    test_gold_earned_on_kill()
    test_shop_upgrade_tick()
    print("All tests passed.")
