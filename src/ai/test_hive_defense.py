import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES, HiveDefenseMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, payload):
        self.events.append((event_type, payload))

class MockBall:
    def __init__(self, id_val, ball_type="normal"):
        self.id = id_val
        self.ball_type = ball_type
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.radius = 20.0
        self.hp = 100.0
        self.team = ""
        self.collected_resources = 0

def test_hive_defense_setup():
    mode = GAME_MODES["hive_defense"]
    world = MockWorld()
    balls = [MockBall("b1"), MockBall("b2"), MockBall("b3"), MockBall("b4")]
    mode.setup(world, balls)

    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

    hives = [h for h in world.arena.hazards if getattr(h, "kind", "") == "hive"]
    assert len(hives) == 2
    assert mode.red_hive is not None
    assert mode.blue_hive is not None
    assert mode.red_hive.hp == 1000.0
    assert mode.blue_hive.hp == 1000.0

def test_hive_defense_tick_resource_spawn():
    mode = HiveDefenseMode()
    world = MockWorld()
    balls = [MockBall("b1"), MockBall("b2")]
    mode.setup(world, balls)

    mode.resource_timer = 0
    mode.tick(world, balls, 0.016)

    resources = [h for h in world.arena.hazards if getattr(h, "kind", "") == "resource_crystal"]
    assert len(resources) == 1

def test_hive_defense_tick_minion_spawn():
    mode = HiveDefenseMode()
    world = MockWorld()
    balls = [MockBall("b1"), MockBall("b2")]
    mode.setup(world, balls)

    mode.minion_timer = 0
    mode.tick(world, balls, 0.016)

    minions = [h for h in world.arena.hazards if getattr(h, "kind", "") == "minion"]
    assert len(minions) == 2  # One per team at level 1

def test_hive_defense_resource_collection_and_deposit():
    mode = HiveDefenseMode()
    world = MockWorld()
    ball = MockBall("b1")
    ball.team = "Red"
    mode.setup(world, [ball])
    ball.team = "Red"

    # Spawn resource near ball
    res = mode.ResourceHazard("res1", ball.x, ball.y)
    world.arena.hazards.append(res)

    mode.tick(world, [ball], 0.016)

    assert ball.collected_resources == 1
    assert not res.active

    # Move ball to hive
    ball.x = mode.red_hive.x
    ball.y = mode.red_hive.y
    mode.tick(world, [ball], 0.016)

    assert ball.collected_resources == 0
    assert mode.red_hive.resources == 1

def test_hive_defense_minion_movement_and_combat():
    mode = HiveDefenseMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    minion = mode.MinionHazard("minion1", "Red", mode.red_hive.x, mode.red_hive.y)
    world.arena.hazards.append(minion)

    mode.tick(world, balls, 1.0) # Move minion

    assert minion.vx != 0 or minion.vy != 0

def test_hive_defense_match_over():
    mode = HiveDefenseMode()
    world = MockWorld()
    mode.setup(world, [])

    mode.red_hive.hp = 0
    mode.tick(world, [], 0.016)

    assert mode.match_over
    assert any(e[0] == "hive_destroyed" and e[1]["team"] == "Red" for e in world.events)
