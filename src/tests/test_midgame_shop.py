import pytest
from ai.game_modes import MazeSafeZoneMode

class DummyBall:
    def __init__(self, bid, x, y, alive=True):
        self.id = bid
        self.x = x
        self.y = y
        self.alive = alive
        self.gold = 0
        self.max_hp = 100
        self.hp = 100
        self.base_speed = 100
        self.speed = 100
        self.base_damage = 10
        self.damage = 10
        self.ball_type = "test"

class DummyWorld:
    def __init__(self):
        self.events = []
        self.arena = None
        self.match_time = 0.0
    def add_event(self, name, data):
        self.events.append((name, data))

def test_gold_earned_on_kill():
    gm = MazeSafeZoneMode()
    world = DummyWorld()
    killer = DummyBall("killer", 0, 0)
    target = DummyBall("target", 10, 10)
    gm.on_ball_died(world, target, killer)
    assert killer.gold == 50
    assert len(world.events) > 0
    assert world.events[0][0] == "gold_earned"

def test_shop_upgrade_tick():
    gm = MazeSafeZoneMode()
    world = DummyWorld()
    # Shop is at 500, 500
    b = DummyBall("shopper", 500, 500)
    b.gold = 150
    gm.tick(world, [b], 0.1)
    assert b.gold == 50
    # verify an upgrade happened
    assert b.max_hp == 120 or b.base_speed == 115 or b.base_damage == 15
    assert any(e[0] == "shop_upgrade" for e in world.events)
