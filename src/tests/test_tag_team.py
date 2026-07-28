import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, **kwargs):
        self.alive = True
        self.traits = []
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, t, d):
        pass
    def _deal_damage(self, t, a):
        pass

def test_ultra_ball_merges_traits_and_sets_timer():
    mode = GAME_MODES["tag_team"]
    world = MockWorld()

    b1 = MockBall(x=10, y=10)
    b1.id = 1
    b1.team = "players"
    b1.ball_type = "player"
    b1.traits = ["fire"]

    b2 = MockBall(x=20, y=20)
    b2.id = 2
    b2.team = "players"
    b2.ball_type = "player"
    b2.traits = ["wind"]

    balls = [b1, b2]

    mode.setup(world, balls)

    b1.ball_type = "player"
    b2.ball_type = "spectator"

    # Simulate a hit
    b1.tag_recent_hit_timer = 1.0
    b1.tag_combo_chain = 2

    # Tick to process hit
    mode.tick(world, balls, 0.016)

    # Simulate swap
    mode.swap_timer = 100.0

    mode.tick(world, balls, 0.016)

    assert getattr(b2, "ultra_ball_timer", 0.0) == 10.0
    assert getattr(b1, "ultra_ball_timer", 0.0) == 10.0

    assert set(b1.traits) == {"fire", "wind"}
    assert set(b2.traits) == {"fire", "wind"}

def test_ultra_ball_expiration_restores_original_traits():
    mode = GAME_MODES["tag_team"]
    world = MockWorld()

    b1 = MockBall(x=10, y=10)
    b1.id = 1
    b1.team = "players"
    b1.ball_type = "player"
    b1.traits = ["fire"]

    b2 = MockBall(x=20, y=20)
    b2.id = 2
    b2.team = "players"
    b2.ball_type = "player"
    b2.traits = ["wind"]

    balls = [b1, b2]

    mode.setup(world, balls)

    # Force ultra ball state
    b1.tag_original_traits = ["fire"]
    b1.traits = ["fire", "wind"]
    b1.ultra_ball_timer = 0.01

    mode.tick(world, balls, 0.016)

    assert b1.ultra_ball_timer == 0.0
    assert set(b1.traits) == {"fire"}
