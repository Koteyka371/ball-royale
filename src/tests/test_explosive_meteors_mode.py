import sys
sys.path.insert(0, 'src')
from ai.game_modes import ExplosiveMeteorsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y, ball_type="brawler"):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.ball_type = ball_type

    def take_damage(self, amount):
        self.hp -= amount

def test_explosive_meteors():
    import random
    random.seed(42)
    mode = ExplosiveMeteorsMode()
    world = MockWorld()

    player1 = MockBall(500, 500)
    spectator = MockBall(500, 500, ball_type="spectator")

    balls = [player1, spectator]

    mode.setup(world, balls)

    # Move timer forward to spawn meteor
    mode.meteor_timer = 1.9
    mode.tick(world, balls, delta=0.2)

    assert len(mode.active_meteors) == 1
    meteor = mode.active_meteors[0]

    # Check indicator hazard created
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "explosive_meteor_indicator"

    # Ensure event was added
    assert len(world.events) == 1
    assert world.events[0][0] == "visual_effect"
    assert world.events[0][1]["type"] == "meteor_warning"

    # Position balls precisely where meteor spawned to guarantee hit
    player1.x = meteor["x"]
    player1.y = meteor["y"]
    spectator.x = meteor["x"]
    spectator.y = meteor["y"]

    # Tick to make it drop
    mode.tick(world, balls, delta=3.0)

    # Verify player took damage, but spectator didn't
    assert player1.hp == 40.0 # 100 - 60
    assert spectator.hp == 100.0

    # Verify meteor is gone
    assert len(mode.active_meteors) == 0

def test_explosive_meteors_radius():
    import random
    random.seed(43)
    mode = ExplosiveMeteorsMode()
    world = MockWorld()

    player1 = MockBall(0, 0) # will be moved
    balls = [player1]

    mode.setup(world, balls)

    # Move timer forward to spawn meteor
    mode.meteor_timer = 1.9
    mode.tick(world, balls, delta=0.2)

    meteor = mode.active_meteors[0]

    # Position player outside radius
    player1.x = meteor["x"] + meteor["radius"] + 10.0
    player1.y = meteor["y"]

    # Tick to make it drop
    mode.tick(world, balls, delta=3.0)

    # Verify player did not take damage
    assert player1.hp == 100.0
