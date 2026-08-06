import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        pass

class MockBall:
    def __init__(self, x=0, y=0, radius=15.0, hp=100.0, alive=True, ball_type="basic", stamina=100.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type
        self.stamina = stamina

def test_ghost_orb_spawn_on_death():
    mode = GAME_MODES["ghost_orb"]
    world = MockWorld()
    balls = [MockBall(x=100, y=100)]

    mode.setup(world, balls)

    # Simulate death
    victim = balls[0]
    victim.alive = False
    mode.on_ball_died(world, victim)

    assert len(mode.ghost_orbs) == 1
    assert len(world.arena.hazards) == 1

    orb = mode.ghost_orbs[0]
    assert orb.x == 100
    assert orb.y == 100
    assert orb.kind == "ghost_orb"

def test_ghost_orb_chase_and_drain():
    mode = GAME_MODES["ghost_orb"]
    world = MockWorld()

    b1 = MockBall(x=100, y=100, alive=True)
    b2 = MockBall(x=200, y=200, alive=True)
    b3 = MockBall(x=500, y=500, alive=False)  # Dead ball shouldn't be chased

    balls = [b1, b2, b3]

    mode.setup(world, balls)

    # Add an orb manually at 150, 150
    orb = mode.GhostOrb(150, 150)
    mode.ghost_orbs.append(orb)

    # Tick with large delta to see movement
    mode.tick(world, balls, delta=1.0)

    # Distance from 150,150 to 100,100 is ~70.7. Distance to 200,200 is also ~70.7.
    # It will pick the first one in the list (b1) since dist < min_dist (strict less than)

    # Let's verify it moved. Speed is 100, so it should move by 100 along the vector to b1
    assert orb.x < 150
    assert orb.y < 150

    # Now test collision stamina drain
    b1.x = orb.x
    b1.y = orb.y
    b1.stamina = 100.0

    mode.tick(world, balls, delta=1.0)

    assert b1.stamina == 50.0  # 100 - 50*1.0

    mode.tick(world, balls, delta=1.0)
    assert b1.stamina == 0.0

def test_ghost_orb_ignore_spectator():
    mode = GAME_MODES["ghost_orb"]
    world = MockWorld()

    spectator = MockBall(x=100, y=100, alive=True, ball_type="spectator")
    balls = [spectator]

    mode.setup(world, balls)
    orb = mode.GhostOrb(150, 150)
    mode.ghost_orbs.append(orb)

    mode.tick(world, balls, delta=1.0)

    # Should not move because no valid targets
    assert orb.x == 150
    assert orb.y == 150
