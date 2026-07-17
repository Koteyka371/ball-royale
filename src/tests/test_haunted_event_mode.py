import pytest
from ai.game_modes import HauntedEventMode

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val):
        self.id = id_val
        self.alive = True
        self.ball_type = "basic"
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.hide_hp_bar = False
        self.hide_team_color = False

def test_haunted_event_mode():
    mode = HauntedEventMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b3.ball_type = "spectator"

    # Test Setup
    mode.setup(world, [b1, b2, b3])
    assert getattr(world.arena, "is_night", False) == True

    # Test Tick logic
    world.arena.is_night = False

    # Make b1 move, b2 stationary
    b1.vx = 10.0

    # Run tick
    mode.tick(world, [b1, b2, b3], delta=0.5)

    assert getattr(world.arena, "is_night", False) == True
    assert getattr(b1, "hide_hp_bar", False) == True
    assert getattr(b1, "hide_team_color", False) == True
    assert getattr(b2, "hide_hp_bar", False) == True
    assert getattr(b3, "hide_hp_bar", False) == False # spectator should not be affected

    # Check trail spawned
    trails = [h for h in world.arena.hazards if getattr(h, "kind", "") == "phantom_trail"]
    assert len(trails) == 1
    assert getattr(trails[0], "x", -1) == b1.x
    assert getattr(trails[0], "y", -1) == b1.y

    # Test clone spawn
    mode.tick(world, [b1, b2, b3], delta=4.5)
    clones = [h for h in world.arena.hazards if getattr(h, "kind", "") == "fireball" and getattr(h, "cosmetic", "") == "spectral"]
    assert len(clones) == 1
    assert getattr(clones[0], "damage", -1) == 0.0
