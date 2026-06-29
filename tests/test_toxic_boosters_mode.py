import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=0, y=0, hp=100.0, alive=True, ball_type="normal"):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type
        self.radius = 10.0
        self.immune_timer = 0.0
        self.team = "TeamA"

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.arena = type("Arena", (object,), {"width": 1000, "height": 1000})()

def test_toxic_boosters_mode_in_dict():
    assert "toxic_boosters" in GAME_MODES

def test_toxic_boosters_damage():
    mode = GAME_MODES["toxic_boosters"]
    world = MockWorld()
    b1 = MockBall(hp=100.0)
    balls = [b1]

    mode.setup(world, balls)

    mode.tick(world, balls, 1.0)

    assert b1.hp < 100.0, "Ball should take damage"
    assert b1.hp == 95.0, "Ball should take 5.0 damage per second"

def test_toxic_boosters_immunity():
    mode = GAME_MODES["toxic_boosters"]
    world = MockWorld()
    b1 = MockBall(hp=100.0)
    b1.immune_timer = 2.0
    balls = [b1]

    mode.setup(world, balls)

    mode.tick(world, balls, 1.0)

    assert b1.hp == 100.0, "Ball should not take damage while immune"
    assert b1.immune_timer == 1.0, "Immune timer should decrement"

def test_toxic_boosters_spawn_and_collect():
    mode = GAME_MODES["toxic_boosters"]
    world = MockWorld()
    b1 = MockBall(x=500, y=500, hp=100.0)
    balls = [b1]

    mode.setup(world, balls)

    # Tick enough to spawn a booster
    mode.tick(world, balls, 3.0)

    # Assert booster was spawned
    assert len(world.boosters) == 1
    booster = world.boosters[0]
    assert (booster.get("kind") if isinstance(booster, dict) else getattr(booster, "kind", None)) == "immune_booster"

    # Move ball to booster
    b1.x = booster.get("x") if isinstance(booster, dict) else booster.x
    b1.y = booster.get("y") if isinstance(booster, dict) else booster.y

    # Tick again
    mode.tick(world, balls, 0.1)

    # Assert booster collected and immunity granted
    assert len(world.boosters) == 0
    assert b1.immune_timer == 5.0
