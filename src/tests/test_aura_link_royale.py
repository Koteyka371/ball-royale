import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

class DummyBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.radius = 20.0
        self.team = ""
        self.killer = None
        self.aura_color = None

class DummyWorld:
    def __init__(self):
        self.weekly_mutator = ""
        class Arena:
            hazards = []
            def get_hazard_by_id(self, *args): return None
        self.arena = Arena()
        self.time = 0.0

def test_aura_link_royale_setup():
    mode = GAME_MODES["aura_link_royale"]
    world = DummyWorld()
    balls = [DummyBall(1, 0, 0), DummyBall(2, 10, 10), DummyBall(3, 20, 20)]

    mode.setup(world, balls)
    for b in balls:
        assert getattr(b, "aura_color") in ["Red", "Blue", "Green"]
        assert b.team == f"Aura {b.aura_color}"

def test_aura_link_royale_tick_damage():
    mode = GAME_MODES["aura_link_royale"]
    world = DummyWorld()

    b1 = DummyBall(1, 0, 0)
    b2 = DummyBall(2, 100, 0)

    target = DummyBall(3, 50, 0)

    b1.aura_color = "Red"
    b2.aura_color = "Red"
    target.aura_color = "Blue"

    balls = [b1, b2, target]

    mode.tick(world, balls, delta=1.0)

    assert target.hp == 100.0 - 50.0
    assert getattr(target, "killer") == 1

def test_aura_link_royale_tick_no_damage_to_same_aura():
    mode = GAME_MODES["aura_link_royale"]
    world = DummyWorld()

    b1 = DummyBall(1, 0, 0)
    b2 = DummyBall(2, 100, 0)

    target = DummyBall(3, 50, 0)

    b1.aura_color = "Red"
    b2.aura_color = "Red"
    target.aura_color = "Red"

    balls = [b1, b2, target]

    mode.tick(world, balls, delta=1.0)

    assert target.hp == 100.0
    assert target.killer is None

def test_aura_link_royale_tick_no_damage_outside_tether():
    mode = GAME_MODES["aura_link_royale"]
    world = DummyWorld()

    b1 = DummyBall(1, 0, 0)
    b2 = DummyBall(2, 100, 0)

    target = DummyBall(3, 50, 100)  # far away

    b1.aura_color = "Red"
    b2.aura_color = "Red"
    target.aura_color = "Blue"

    balls = [b1, b2, target]

    mode.tick(world, balls, delta=1.0)

    assert target.hp == 100.0
    assert target.killer is None
