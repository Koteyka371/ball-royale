import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick_timer = 1.0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, ball_id, x, y, team, ball_type="normal"):
        self.id = ball_id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.shield = 0
        self.damage = 10
        self.base_damage = 10
        self.score = 0
        self.invulnerable_timer = 0.0
        self.ultimate_charge = 0.0
        self.max_ultimate_charge = 100.0
        self.inventory = []

@pytest.fixture
def mode():
    m = GAME_MODES["battle_royale"]
    m.high_tier_supply_drop_timer = 0.0
    m.active_telegraphs = []
    m.high_tier_drops = []
    return m

def test_setup(mode):
    world = MockWorld()
    balls = [MockBall(1, 100, 100, "Red")]
    mode.setup(world, balls)
    assert mode.high_tier_supply_drop_timer == 0.0
    assert len(mode.active_telegraphs) == 0

def test_tick_spawns_telegraph(mode):
    world = MockWorld()
    balls = [MockBall(1, 100, 100, "Red")]
    mode.setup(world, balls)

    # Tick for 30 seconds to trigger spawn
    for _ in range(300):
        mode.tick(world, balls, 0.1)

    assert len(mode.active_telegraphs) == 1
    t = mode.active_telegraphs[0]
    assert abs(t["timer"] - 4.9) < 0.001

    # Battle Royale mode spawns obstacles, so hazard count > 0
    telegraphs = [h for h in world.arena.hazards if getattr(h, "kind", "") == "supply_drop_telegraph"]
    assert len(telegraphs) == 1
    assert "high_tier_drop_telegraph" in [e[0] for e in world.events]

def test_telegraph_to_drop(mode):
    world = MockWorld()
    balls = [MockBall(1, 100, 100, "Red")]
    mode.setup(world, balls)

    mode.high_tier_supply_drop_timer = 29.9 # next tick will spawn telegraph
    mode.tick(world, balls, 0.2)

    assert len(mode.active_telegraphs) == 1

    # Tick for 5 seconds to trigger drop
    for _ in range(50):
        mode.tick(world, balls, 0.1)

    assert len(mode.active_telegraphs) == 0
    assert len(mode.high_tier_drops) == 1
    assert "high_tier_drop_spawn" in [e[0] for e in world.events]

def test_capture_drop(mode):
    world = MockWorld()
    b = MockBall(1, 500, 500, "Red")
    balls = [b]
    mode.setup(world, balls)

    mode.high_tier_supply_drop_timer = 29.9
    mode.tick(world, balls, 0.2)

    # Manually move telegraph to ball position so drop spawns on it
    mode.active_telegraphs[0]["x"] = 500
    mode.active_telegraphs[0]["y"] = 500

    for _ in range(50):
        mode.tick(world, balls, 0.1)

    assert len(mode.high_tier_drops) == 1
    drop = mode.high_tier_drops[0]

    # It should take 5 seconds to capture (100 / 20 = 5)
    for _ in range(55):
        mode.tick(world, balls, 0.1)

    assert not getattr(drop, "active", True) or len(mode.high_tier_drops) == 0 or not drop in world.arena.hazards
