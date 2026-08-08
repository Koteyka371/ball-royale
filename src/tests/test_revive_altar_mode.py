import pytest
from unittest.mock import MagicMock
from ai.game_modes import GameMode, GAME_MODES, ReviveAltarMode

@pytest.fixture
def mode():
    return ReviveAltarMode()

@pytest.fixture
def world():
    w = MagicMock()
    del w.leaderboard_manager
    del w.profile_manager
    w.arena = MagicMock()
    w.arena.width = 1000.0
    w.arena.height = 1000.0
    w.arena.items = []
    return w

class DummyBall:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "silence_timer"):
            self.silence_timer = 0.0
        if not hasattr(self, "vx"):
            self.vx = 10.0
        if not hasattr(self, "vy"):
            self.vy = 10.0

def test_revive_altar_setup(mode, world):
    mode.setup(world, [])
    assert len(world.revive_altars) == 1
    assert world.revive_altars[0]["x"] == 500.0
    assert world.revive_altars[0]["y"] == 500.0
    assert world.revive_altars[0]["radius"] == 100.0
    assert world.revive_altars[0]["progress"] == 0.0
    assert world.revive_altars[0]["channeling_ball"] is None

def test_revive_altar_token_spawn(mode, world):
    mode.setup(world, [])
    mode.tick(world, [], delta=11.0)
    # Should spawn a token
    assert len(world.arena.items) == 1
    item = world.arena.items[0]
    assert item["kind"] == "revive_token"
    assert item["active"] == True

def test_revive_altar_token_pickup(mode, world):
    mode.setup(world, [])
    # Setup ball and token
    b1 = DummyBall(alive=True, has_revive_token=False, team="A", x=200.0, y=200.0, radius=10.0)
    world.arena.items.append({
        "kind": "revive_token",
        "x": 200.0,
        "y": 200.0,
        "radius": 15.0,
        "active": True
    })

    # Force spawn timer so it doesn't spawn another one during tick
    mode.token_spawn_timer = 100.0

    mode.tick(world, [b1], delta=0.1)

    assert b1.has_revive_token == True
    assert len(world.arena.items) == 0 # Item should be removed

def test_revive_altar_channel_and_revive(mode, world):
    mode.setup(world, [])
    b1 = DummyBall(alive=True, has_revive_token=True, team="A", x=500.0, y=500.0, radius=10.0, silence_timer=0.0, vx=10.0, vy=10.0)
    b2 = DummyBall(alive=False, team="A", max_hp=100.0, x=0.0, y=0.0)
    balls = [b1, b2]

    # Force tick past spawn
    mode.token_spawn_timer = 100.0

    mode.tick(world, balls, delta=0.5)

    # Should start channeling
    assert b1.silence_timer >= 0.5
    assert world.revive_altars[0]["channeling_ball"] == id(b1)

    # Check slow
    assert b1.vx == 5.0
    assert b1.vy == 5.0

    # Fast forward to finish channel
    mode.tick(world, balls, delta=3.0)

    # b2 should be revived
    assert b2.alive == True
    assert b2.hp == 50.0
    assert b2.x == 500.0
    assert b2.y == 500.0
    assert getattr(b2, "intangible", False) == True
    assert getattr(b2, "intangible_timer", 0.0) == 2.0

    # b1 loses token
    assert b1.has_revive_token == False

    # Altar resets
    assert world.revive_altars[0]["progress"] == 0.0
    assert world.revive_altars[0]["channeling_ball"] is None

def test_game_modes_registration():
    assert "revive_altar" in GAME_MODES
    assert isinstance(GAME_MODES["revive_altar"], ReviveAltarMode)
