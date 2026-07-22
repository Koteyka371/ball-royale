import pytest
from ai.game_modes import RevenantMode

class MockBall:
    def __init__(self, bid, x, y, hp=100.0, alive=True):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = alive
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.is_ghost = False

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []
    def add_event(self, name, payload):
        self.events.append((name, payload))

def test_revenant_ghost_conversion():
    mode = RevenantMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, hp=0.0) # Dead but alive=True
    b1.last_attacker_id = 2
    b2 = MockBall(2, 50, 50, hp=100.0)

    balls = [b1, b2]
    mode.setup(world, balls)
    mode.tick(world, balls)

    # b1 should be a ghost
    assert b1.is_ghost == True
    assert b1.alive == True
    assert b1.hp == 50.0
    assert b1.max_hp == 50.0
    assert b1.speed == 70.0 # 100 * 0.7
    assert b1.damage == 5.0 # 10 * 0.5
    assert b1.killer_id == 2
    assert getattr(b1, "ghost_damage_dealt", None) == 0.0

def test_revenant_revive_on_assist():
    mode = RevenantMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, hp=50.0)
    b1.is_ghost = True
    b1.killer_id = 2
    b1.ghost_damage_dealt = 0.0
    b2 = MockBall(2, 50, 50, hp=100.0) # Killer
    b3 = MockBall(3, 100, 100, hp=0.0) # New victim of b2
    b3.last_attacker_id = 2

    balls = [b1, b2, b3]
    # world.dead_balls starts empty
    mode.tick(world, balls)

    # In the first tick, b3 dies and gets converted to ghost
    assert b3.is_ghost == True
    assert b3.killer_id == 2
    # Wait, does b1 revive?
    # b3 was just converted to ghost, so it didn't fully die.
    # Therefore it is NOT added to world.dead_balls.
    # If world.dead_balls didn't increase with a kill by b2, b1 doesn't revive.
    assert b1.is_ghost == True

    # Now make b3 a ghost that fully dies.
    b3.hp = 0.0 # ghost dying
    b3.last_attacker_id = 2 # killed by b2 again
    mode.tick(world, balls)

    # b3 fully dies, added to world.dead_balls
    assert b3.alive == False
    assert 3 in world.dead_balls

    # Next tick, b1 sees b2 got a kill
    mode.tick(world, balls)
    assert b1.is_ghost == False
    assert b1.hp == 100.0
    assert b1.speed == 100.0

def test_revenant_revive_on_killer_death():
    mode = RevenantMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, hp=50.0)
    b1.is_ghost = True
    b1.killer_id = 2
    b2 = MockBall(2, 50, 50, hp=100.0)

    balls = [b1, b2]
    mode.tick(world, balls)
    assert b1.is_ghost == True

    b2.alive = False # killer dies
    mode.tick(world, balls)
    assert b1.is_ghost == False # revived

def test_revenant_revive_on_chip_damage():
    mode = RevenantMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, hp=50.0)
    b1.is_ghost = True
    b1.killer_id = 2
    b1.ghost_damage_dealt = 0.0

    b2 = MockBall(2, 500, 500, hp=100.0) # killer far away
    b3 = MockBall(3, 10, 10, hp=100.0) # enemy close by

    balls = [b1, b2, b3]
    mode.tick(world, balls)

    # simulate b3 taking damage
    b3.hp = 20.0 # 80 damage taken

    mode.tick(world, balls)
    # b1 was close, so b1.ghost_damage_dealt should go up by 80
    # threshold is 50, so b1 should revive
    assert b1.is_ghost == False
    assert getattr(b1, "ghost_damage_dealt", 0) == 0.0

def test_revenant_tether_pull():
    mode = RevenantMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, hp=50.0)
    b1.is_ghost = True
    b1.killer_id = 2
    b1.ghost_damage_dealt = 0.0

    b2 = MockBall(2, 500, 0, hp=100.0) # Killer is >400 distance away

    balls = [b1, b2]
    mode.tick(world, balls)

    # b1 should be pulled towards b2
    assert b1.vx > 0
    assert b1.vy == 0
