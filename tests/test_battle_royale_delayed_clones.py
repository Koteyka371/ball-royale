import pytest
from ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = self.balls
        self.boosters = []
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.speed = 100.0
        self.damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "team1"
        self.mass = 1.0

def test_delayed_clones_event():
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    world.balls.append(b1)

    mode = BattleRoyaleMode()
    mode.setup(world, world.balls)

    # Force event to be delayed clones
    class MockRandom:
        def choice(self, lst):
            return "delayed_clones"
        def uniform(self, a, b):
            return a
        def randint(self, a, b):
            return a
        def random(self):
            return 0.5
    mode.random = MockRandom()

    # Trigger event
    mode.tick(world, world.balls, delta=25.0)

    clones = [b for b in world.balls if getattr(b, "is_delayed_clone", False)]
    assert len(clones) == 1
    assert any(e[0] == "delayed_clones" for e in world.events)

    clone = clones[0]
    assert clone.owner_id == b1.id

    # Test delayed mimicry
    b1.vx = 50.0
    b1.vy = 0.0

    # Needs to hit action history limit
    for i in range(35):
        mode.tick(world, world.balls, delta=0.016)

    # Clone should now have caught up to the delayed vx
    assert clone.vx == 50.0
    assert clone.vy == 0.0

    # Test destruction if owner dies
    b1.hp = 0
    b1.alive = False

    mode.tick(world, world.balls, delta=0.1)

    assert clone.hp == 0
    assert clone.alive == False
