import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.capture_the_flag_elements_in_battle_royale import CaptureTheFlagElementsInBattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.has_flag = False
        self.base_speed = 90.0
        self.speed = 90.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_ctf_br_setup():
    mode = CaptureTheFlagElementsInBattleRoyaleMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)

    assert len(world.boosters) == 4
    for b in world.boosters:
        assert b.is_flag == True
        assert b.team == "Neutral"

def test_ctf_br_tick():
    mode = CaptureTheFlagElementsInBattleRoyaleMode()
    world = MockWorld()

    # Ball 1 inside center zone but no flag
    b1 = MockBall(1, 500, 500)

    # Ball 2 outside center zone with flag
    b2 = MockBall(2, 100, 100)
    b2.has_flag = True

    # Ball 3 inside center zone with flag
    b3 = MockBall(3, 500, 500)
    b3.has_flag = True

    world.balls = [b1, b2, b3]

    mode.setup(world, world.balls)
    mode.tick(world, 0.1)

    # Ball 1 should not be boosted
    assert b1.base_speed <= 180.0

    # Ball 2 should not be boosted
    assert b2.base_speed <= 180.0
    assert b2.has_flag == True

    # Ball 3 should be boosted
    assert b3.has_flag == False
    assert b3.base_speed > 150.0
    assert b3.base_damage >= 30.0
    assert b3.hp == 600.0
    assert b3.max_hp == 600.0
    assert 3 in mode.boosted_players
    assert len(world.events) > 0
    assert world.events[0][0] == "flag_captured_center"

def test_ctf_br_tick_already_boosted():
    mode = CaptureTheFlagElementsInBattleRoyaleMode()
    world = MockWorld()
    b3 = MockBall(3, 500, 500)
    b3.has_flag = True
    world.balls = [b3]

    mode.setup(world, world.balls)
    mode.tick(world, 0.1)

    assert b3.base_speed > 150.0

    # Bring another flag, but shouldn't boost again since it's in boosted_players
    b3.has_flag = True
    mode.tick(world, 0.1)

    assert b3.base_speed > 150.0
