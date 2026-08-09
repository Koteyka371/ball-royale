import pytest
from unittest.mock import MagicMock
from ai.game_modes import CorruptedCapturePointsMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_name, data):
        self.events.append((event_name, data))

class MockBall:
    def __init__(self, id_val, team, x, y):
        self.id = id_val
        self.team = team
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.alive = True
        self.kills = 0
        self.damage_multiplier = 1.0
        self.has_corrupted_buff = False

def test_spawn_capture_point():
    mode = CorruptedCapturePointsMode()
    world = MockWorld()

    # Tick past spawn timer
    mode.tick(world, [], 11.0)

    assert len(mode.capture_points) == 1
    cp = mode.capture_points[0]
    assert cp["owner_team"] is None
    assert cp["capture_progress"] == 0.0

    event_names = [e[0] for e in world.events]
    assert "corrupted_point_spawned" in event_names

def test_capture_and_buff_application():
    mode = CorruptedCapturePointsMode()
    world = MockWorld()

    mode.tick(world, [], 11.0)
    cp = mode.capture_points[0]
    cp["x"] = 500.0
    cp["y"] = 500.0

    # Ball from Team A inside radius
    ball_a = MockBall(1, "A", 500.0, 500.0)
    balls = [ball_a]

    # Tick to fully capture
    for _ in range(5): # 20 progress per tick (delta=1.0 for test) -> 5 ticks to 100
        mode.tick(world, balls, 1.0)

    # Point should be removed after capture
    assert len(mode.capture_points) == 0


    # Check buff applied
    assert ball_a.has_corrupted_buff is True
    assert ball_a.damage_multiplier == 3.0
    assert getattr(ball_a, "corrupted_buff_kills_base", -1) == 0

def test_continuous_health_drain():
    mode = CorruptedCapturePointsMode()
    world = MockWorld()

    ball = MockBall(1, "A", 100.0, 100.0)
    ball.has_corrupted_buff = True
    ball.corrupted_buff_kills_base = 0
    ball.kills = 0
    ball.base_damage_multiplier = 1.0
    ball.damage_multiplier = 3.0

    # Tick to drain health
    mode.tick(world, [ball], 1.0)

    assert ball.hp == 80.0 # 100.0 - (20.0 * 1.0)

def test_buff_removal_on_kill():
    mode = CorruptedCapturePointsMode()
    world = MockWorld()

    ball = MockBall(1, "A", 100.0, 100.0)
    ball.has_corrupted_buff = True
    ball.corrupted_buff_kills_base = 0
    ball.kills = 1 # Got a kill
    ball.base_damage_multiplier = 1.0
    ball.damage_multiplier = 3.0

    # Tick to clear buff
    mode.tick(world, [ball], 1.0)

    assert ball.has_corrupted_buff is False
    assert ball.damage_multiplier == 1.0
    assert ball.hp == 100.0 # HP should NOT be drained on the tick it clears

    event_names = [e[0] for e in world.events]
    assert "corrupted_buff_cleared" in event_names

def test_death_from_drain():
    mode = CorruptedCapturePointsMode()
    world = MockWorld()

    ball = MockBall(1, "A", 100.0, 100.0)
    ball.has_corrupted_buff = True
    ball.corrupted_buff_kills_base = 0
    ball.kills = 0
    ball.hp = 10.0 # Low HP

    mode.tick(world, [ball], 1.0) # Drain by 20 -> dies

    assert ball.hp == 0
    assert ball.alive is False
    assert ball.has_corrupted_buff is False

    event_names = [e[0] for e in world.events]
    assert "ball_died" in event_names
