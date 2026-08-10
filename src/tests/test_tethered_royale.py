import pytest
from ai.game_modes import TetheredRoyaleMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

    def _deal_damage(self, attacker, target, amount):
        target.hp -= amount

class MockBall:
    def __init__(self, id_val, team_val):
        self.id = id_val
        self.team = team_val
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.ball_type = "default"

def test_tethered_royale_setup():
    mode = TetheredRoyaleMode()
    world = MockWorld()
    balls = [MockBall(1, 1), MockBall(2, 2), MockBall(3, 3), MockBall(4, 4)]

    mode.setup(world, balls)

    # Assert tethers are symmetric and hp is combined
    assert len(mode.tethers) == 4
    for b in balls:
        assert hasattr(b, "tether_target")
        assert getattr(b, "hp") == 200.0
        assert getattr(b, "max_hp") == 200.0

def test_tethered_royale_tether_pull():
    mode = TetheredRoyaleMode()
    world = MockWorld()
    b1 = MockBall(1, 1)
    b2 = MockBall(2, 2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Move them far apart
    b1.x, b1.y = 0.0, 0.0
    b2.x, b2.y = 400.0, 0.0

    # Since dist (400) > max_dist (300), they should pull towards each other
    mode.tick(world, balls, 0.016)

    assert b1.vx > 0.0
    assert b2.vx < 0.0

def test_tethered_royale_chain_damage():
    mode = TetheredRoyaleMode()
    world = MockWorld()
    b1 = MockBall(1, 1)
    b2 = MockBall(2, 2)
    b3 = MockBall(3, 3) # Enemy in middle
    b4 = MockBall(4, 4)
    balls = [b1, b2, b3, b4]

    # We want b1 and b2 to be tethered
    # Let's bypass setup and set it manually for test predictability
    mode.tethers = {1: b2, 2: b1, 3: b4, 4: b3}
    mode.prev_alive = {1: True, 2: True, 3: True, 4: True}
    mode.prev_hp = {1: 200.0, 2: 200.0, 3: 200.0, 4: 200.0}
    b1.tether_target = b2
    b2.tether_target = b1
    b3.tether_target = b4
    b4.tether_target = b3

    b1.hp = b2.hp = 200.0
    b3.hp = b4.hp = 200.0

    # Position balls
    b1.x, b1.y = 0.0, 0.0
    b2.x, b2.y = 400.0, 0.0
    b3.x, b3.y = 200.0, 0.0
    b4.x, b4.y = 200.0, 200.0

    mode.tick(world, balls, 0.016)

    # Check chain damage applied to b3 (it's between b1 and b2)
    assert b3.hp < 200.0

def test_tethered_royale_death_break():
    mode = TetheredRoyaleMode()
    world = MockWorld()
    b1 = MockBall(1, 1)
    b2 = MockBall(2, 2)
    balls = [b1, b2]

    mode.setup(world, balls)
    b1.base_max_hp = 100.0
    b2.base_max_hp = 100.0

    assert b2.tether_target == b1
    assert b2.max_hp == 200.0

    # b1 dies
    b1.alive = False
    mode.tick(world, balls, 0.016)

    assert b2.tether_target is None
    assert b2.max_hp == 100.0
