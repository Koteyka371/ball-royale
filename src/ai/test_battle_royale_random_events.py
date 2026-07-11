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

def test_loot_goblin_event():
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    world.balls.append(b1)

    mode = BattleRoyaleMode()
    mode.setup(world, world.balls)

    # Force event to be loot goblin
    class MockRandom:
        def choice(self, lst):
            return "loot_goblin"
        def uniform(self, a, b):
            return a
        def randint(self, a, b):
            return a
        def random(self):
            return 0.1
    mode.random = MockRandom()

    # Trigger event
    mode.tick(world, world.balls, delta=25.0)

    goblins = [b for b in world.balls if getattr(b, "ball_type", None) == "loot_goblin"]
    assert len(goblins) == 1
    assert any(e[0] == "loot_goblin_spawn" for e in world.events)

    goblin = goblins[0]
    # Test that it runs away from player
    goblin.x = 200
    goblin.y = 100
    b1.x = 100
    b1.y = 100
    mode.tick(world, world.balls, delta=0.1)
    assert goblin.vx > 0  # Should run away to the right

    # Test that it drops loot when killed
    goblin.hp = 0
    mode.tick(world, world.balls, delta=0.1)
    assert not goblin.alive
    assert len(world.boosters) >= 3

def test_low_gravity_event():
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    world.balls.append(b1)

    mode = BattleRoyaleMode()
    mode.setup(world, world.balls)

    class MockRandom:
        def choice(self, lst):
            return "low_gravity_zone"
        def uniform(self, a, b):
            return a
        def randint(self, a, b):
            return a
        def random(self):
            return 0.1
    mode.random = MockRandom()

    # Trigger event
    mode.tick(world, world.balls, delta=25.0)

    hazards = world.arena.hazards
    low_gravs = [h for h in hazards if getattr(h, "kind", "") == "low_gravity_zone"]
    assert len(low_gravs) == 1
    assert any(e[0] == "low_gravity_zone" for e in world.events)

    # Test that it reduces mass
    b1._low_grav_applied = False
    if hasattr(b1, "original_mass"):
        delattr(b1, "original_mass")
    b1.mass = 2.0
    low_gravs[0].x = b1.x
    low_gravs[0].y = b1.y
    # Inside zone
    mode.tick(world, world.balls, delta=0.1)
    # Make sure we didn't just check immediately
    assert b1.mass == 1.0  # Half of 2.0

    # Move outside
    b1.x = 900
    mode.tick(world, world.balls, delta=0.1)
    assert b1.mass == 2.0  # Restored
