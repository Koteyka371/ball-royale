import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []
        self.boosters = []
        self.next_id = 1000

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id_val, btype="warrior"):
        self.id = id_val
        self.ball_type = btype
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = btype

    @property
    def position(self):
        return self

def test_supply_drop_safe_zone_setup():
    mode = GAME_MODES["supply_drop_safe_zone"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(5)]
    mode.setup(world, balls)

    assert mode.drop_timer == 0.0
    assert hasattr(world, "boosters")
    assert len(world.boosters) == 0

def test_supply_drop_safe_zone_tick_spawns_drops():
    mode = GAME_MODES["supply_drop_safe_zone"]
    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    # Tick below 10s should not spawn drop
    mode.tick(world, balls, delta=5.0)
    assert len(world.boosters) + len(world.arena.hazards) == 0

    # Tick above 10s total should spawn a drop
    mode.tick(world, balls, delta=6.0)

    # Can be either a booster or a hazard
    total_drops = len(world.boosters) + len(world.arena.hazards)
    assert total_drops == 1
