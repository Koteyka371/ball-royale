import sys
sys.path.append("src")
from ai.game_modes import GameMode, GAME_MODES
from ai.mercenary_outposts import MercenaryOutpostsMode, MercenaryBall, MercenaryOutpostHazard
import math

class MockBall:
    def __init__(self, bid, x, y, team, ball_type="player"):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True
        self.ball_type = ball_type

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

def test_mercenary_outposts():
    mode = MercenaryOutpostsMode()
    mode.active = True
    mode.active_timer = 5.0
    world = MockWorld()

    player1 = MockBall(1, 300, 300, "Red")
    balls = [player1]

    mode.setup(world, balls)

    hazards = world.arena.hazards
    assert len(hazards) == 2
    outpost = hazards[0]
    assert outpost.kind == "mercenary_outpost"
    assert outpost.capture_progress == 0.0

    # Tick to capture
    outpost.capture_threshold = 1.0 # make it fast
    mode.tick(world, balls, delta=0.5)
    assert outpost.owner_id == 1
    assert outpost.capture_progress == 0.5

    mode.tick(world, balls, delta=0.5)
    assert outpost.capture_progress == 1.0 # fully captured

    # Spawn timer
    outpost.spawn_interval = 2.0
    outpost.spawn_timer = 1.9

    mode.tick(world, balls, delta=0.2) # spawns a merc

    # check new balls
    assert len(balls) == 2
    merc = balls[1]
    assert merc.ball_type == "mercenary"
    assert merc.owner_id == 1
    assert merc.team == "Red"

    # Test apply_dynamic_traits (follow owner)
    player1.x = 800
    player1.y = 800

    mode.apply_dynamic_traits(world, balls, delta=0.1)
    # merc should move towards player1
    assert merc.vx != 0.0 or merc.vy != 0.0
