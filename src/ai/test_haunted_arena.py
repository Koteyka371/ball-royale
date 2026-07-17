import pytest
from ai.game_modes import HauntedArenaMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val, x=100.0, y=100.0, ball_type="normal"):
        self.id = id_val
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = True

def test_haunted_arena_hides_ui():
    mode = HauntedArenaMode()
    world = MockWorld()
    b1 = MockBall(1)
    b1.hide_hp_bar = False
    b1.hide_team_color = False

    # tick without reaching any timer limit
    mode.tick(world, [b1], 0.1)

    assert getattr(b1, "hide_hp_bar", False) is True
    assert getattr(b1, "hide_team_color", False) is True

def test_haunted_arena_phantom_trail():
    mode = HauntedArenaMode()
    world = MockWorld()
    b1 = MockBall(1, x=250.0, y=250.0)

    # Tick 15 times with 0.1s delta (total 1.5s)
    for _ in range(15):
        mode.tick(world, [b1], 0.1)

    # Should spawn one trail
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "phantom_trail"
    assert hazard.x == 250.0
    assert hazard.y == 250.0

def test_haunted_arena_spectral_clone():
    mode = HauntedArenaMode()
    world = MockWorld()

    # Tick 51 times with 0.1s delta (total 5.1s)
    for _ in range(51):
        mode.tick(world, [], 0.1)

    assert len(world.arena.hazards) == 1
    clone = world.arena.hazards[0]
    assert getattr(clone, "kind", "") == "spectral_clone"

    initial_x = clone.x
    initial_y = clone.y
    vx = clone.vx
    vy = clone.vy

    # Tick again to check movement
    delta = 0.5
    mode.tick(world, [], delta)

    # Check if x/y updated according to vx/vy * delta
    assert clone.x == initial_x + vx * delta
    assert clone.y == initial_y + vy * delta
