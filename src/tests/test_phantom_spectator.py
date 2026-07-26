import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
import random

class MockBall:
    def __init__(self, x=0, y=0, radius=10.0, hp=0.0, alive=False):
        self.id = 999
        self.team = "test_team"
        self.ball_type = "basic"
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.speed = 10.0
        self.vx = 0
        self.vy = 0

class MockHazard:
    def __init__(self, x=10, y=0, radius=10.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = "mud"

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard(x=10, y=0)]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

def test_phantom_player():
    ball = MockBall(x=0, y=0, hp=0, alive=False)
    world = MockWorld()
    world.balls = [ball]
    action = Action(ball, world)

    # Tick 1: transform to phantom
    action.execute("idle", 1.0)
    assert ball.ball_type == "phantom"
    assert hasattr(ball, "phantom_spawn_timer")

    # Tick 2: phantom behavior (pushing hazard)
    action.execute("idle", 1.0)
    assert ball.x > 0
    assert world.arena.hazards[0].x > 10

    # Fast forward to trigger spawn
    random.seed(42) # Ensure reproducibility if possible, but testing both is better
    initial_hazards = len(world.arena.hazards)
    initial_boosters = len(world.boosters)

    # Tick down timer (spawn timer is 5.0, we used 2.0 so far)
    action.execute("idle", 4.0)

    assert len(world.arena.hazards) > initial_hazards or len(world.boosters) > initial_boosters

    # Verify the spawn is either ice_patch or health_pack
    spawned_item_valid = False
    if len(world.arena.hazards) > initial_hazards:
        assert world.arena.hazards[-1].kind == "ice_patch"
        spawned_item_valid = True
    elif len(world.boosters) > initial_boosters:
        assert world.boosters[-1]["kind"] == "health_pack"
        spawned_item_valid = True

    assert spawned_item_valid
