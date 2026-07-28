import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y, team="red"):
        self.id = id_val
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.team = team
        self.base_damage = 10.0
        self.attack_speed = 1.0
        self.ball_type = "normal"

class MockArena:
    def __init__(self):
        self.width = 2000
        self.height = 2000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.tick_timer = 1.0

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_telegraphed_supply_drop_setup():
    mode = GAME_MODES["telegraphed_supply_drop"]
    world = MockWorld()
    b = MockBall(1, 100, 100)
    mode.setup(world, [b])

    assert mode.drop_timer == 0.0
    assert mode.active_telegraphs == []
    assert mode.high_tier_drops == []

def test_telegraphed_supply_drop_spawn_telegraph():
    mode = GAME_MODES["telegraphed_supply_drop"]
    world = MockWorld()
    b = MockBall(1, 100, 100)
    mode.setup(world, [b])

    # Tick in small steps to prevent timer bypass
    mode.drop_timer = 19.9
    mode.tick(world, [b], 0.2)

    assert len(mode.active_telegraphs) == 1
    t = mode.active_telegraphs[0]
    assert t["kind"] == "supply_drop_telegraph"
    assert t["timer"] > 4.5

    assert len(world.arena.hazards) == 1
    h = world.arena.hazards[0]
    assert getattr(h, "kind", "") == "supply_drop_telegraph"

def test_telegraphed_supply_drop_spawn_drop():
    mode = GAME_MODES["telegraphed_supply_drop"]
    world = MockWorld()
    b = MockBall(1, 100, 100)
    mode.setup(world, [b])

    mode.drop_timer = 19.9
    mode.tick(world, [b], 0.2)

    # Fast forward telegraph timer
    t = mode.active_telegraphs[0]
    t["timer"] = 0.1
    mode.tick(world, [b], 0.2)

    assert len(mode.active_telegraphs) == 0
    assert len(mode.high_tier_drops) == 1
    drop = mode.high_tier_drops[0]
    assert getattr(drop, "kind", "") == "high_tier_drop"

    # telegraph is removed, drop is added
    assert len(world.arena.hazards) == 1
    assert getattr(world.arena.hazards[0], "kind", "") == "high_tier_drop"

def test_telegraphed_supply_drop_capture():
    mode = GAME_MODES["telegraphed_supply_drop"]
    world = MockWorld()
    b = MockBall(1, 100, 100, "blue")
    mode.setup(world, [b])

    mode.drop_timer = 19.9
    mode.tick(world, [b], 0.2)

    t = mode.active_telegraphs[0]
    t["timer"] = 0.1
    mode.tick(world, [b], 0.2)

    drop = mode.high_tier_drops[0]

    # Move ball to drop
    b.x = getattr(drop, "x", 0.0)
    b.y = getattr(drop, "y", 0.0)

    # Tick to set capturing team
    mode.tick(world, [b], 0.1)

    # Tick to capture completely (100 / 20 = 5 seconds)
    mode.tick(world, [b], 5.1)

    assert getattr(drop, "active", True) == False
    assert drop not in world.arena.hazards

    # One of the buffs should be applied
    assert (
        getattr(b, "invulnerable_timer", 0.0) > 0.0 or
        getattr(b, "ultimate_charge", 0.0) == getattr(b, "max_ultimate_charge", 100.0) or
        getattr(b, "shield", 0.0) > 0.0 or
        getattr(b, "soul_boost_timer", 0.0) > 0.0 or
        getattr(b, "speed_boost_timer", 0.0) > 0.0
    )
