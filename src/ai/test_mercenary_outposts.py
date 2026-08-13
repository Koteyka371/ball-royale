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
        self.radius = 20.0
        self.currency = 0
        self.prestige_tokens = 0
        self.purchase_cooldown = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

def test_mercenary_outposts_spawning_and_hiring():
    mode = MercenaryOutpostsMode()
    mode.active = True
    mode.active_timer = 5.0
    world = MockWorld()

    player1 = MockBall(1, 300, 300, "Red")
    player1.currency = 15
    player1.prestige_tokens = 0
    balls = [player1]

    mode.setup(world, balls)

    hazards = world.arena.hazards
    assert len(hazards) == 2
    outpost = hazards[0]
    assert outpost.kind == "mercenary_outpost"

    # Spawn timer
    outpost.spawn_interval = 2.0
    outpost.spawn_timer = 1.9

    # Trigger spawn
    mode.tick(world, balls, delta=0.2)
    assert len(balls) == 2
    merc = balls[1]
    assert merc.ball_type == "mercenary"
    assert merc.owner_id is None
    assert merc.team is None
    assert merc.hire_timer == 0.0

    # Test hiring with currency
    mode.tick(world, balls, delta=0.1)

    assert merc.owner_id == 1
    assert merc.team == "Red"
    assert merc.hire_timer == 30.0
    assert player1.currency == 5
    assert player1.purchase_cooldown == 1.0

    # Test duration decay
    merc.hire_timer = 0.5
    mode.tick(world, balls, delta=0.6)

    # Should revert to neutral
    assert merc.owner_id is None
    assert merc.team is None
    assert merc.hire_timer == 0.0

def test_mercenary_outposts_hiring_prestige():
    mode = MercenaryOutpostsMode()
    world = MockWorld()

    player1 = MockBall(1, 300, 300, "Red")
    player1.currency = 0
    player1.prestige_tokens = 2
    balls = [player1]

    mode.setup(world, balls)
    hazards = world.arena.hazards
    outpost = hazards[0]
    outpost.spawn_interval = 2.0
    outpost.spawn_timer = 2.0

    # Spawn it first, it won't be hired this tick because hire logic is before spawn logic
    mode.tick(world, balls, delta=0.1)
    # Next tick it will be hired
    mode.tick(world, balls, delta=0.1)

    merc = balls[1]

    assert merc.owner_id == 1
    assert player1.prestige_tokens == 1
