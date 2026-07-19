import pytest
from unittest.mock import MagicMock
from ai.action import Action
from ai.game_modes import GameMode

class MockBall:
    def __init__(self, id=1, x=0, y=0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.hp = 100.0
        self.team = "Red"
        self.ball_type = "normal"

class MockHazard:
    def __init__(self, x=0, y=0, kind="trap"):
        self.x = x
        self.y = y
        self.kind = kind
        self.duration = 10.0
        self.is_detonating = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_black_hole_mine():
    world = MockWorld()
    mode = GameMode()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 0) # within pull radius
    world.balls = [b1, b2]

    mine = MockHazard(0, 0, "trap")
    world.arena.hazards.append(mine)

    action = Action(world, b1)

    # Step on it
    mine.is_detonating = True
    mine.detonation_timer = 3.0

    # Tick should pull
    mode.tick(world, world.balls, 0.1)

    assert mine.detonation_timer < 3.0
    assert mine.is_detonating == True
    assert b2.vx < 0 # Pulled towards 0,0

    # Wait out the timer
    mine.detonation_timer = 0.0

    mode.tick(world, world.balls, 0.1)

    assert mine.duration == 0.0
    assert mine.is_detonating == False
    assert b1.hp < 100.0
    assert b2.hp < 100.0


def test_black_hole_mine_pulls_boosters():
    world = MockWorld()
    mode = GameMode()
    world.boosters = []

    b1 = MockBall(1, 0, 0)
    world.balls = [b1]

    booster = MockBall(2, 50, 0) # Use MockBall as a proxy for booster to have x,y,vx,vy
    world.boosters.append(booster)

    mine = MockHazard(0, 0, "trap")
    world.arena.hazards.append(mine)

    # Step on it
    mine.is_detonating = True
    mine.detonation_timer = 3.0

    # Tick should pull
    mode.tick(world, world.balls, 0.1)

    assert booster.vx < 0 # Pulled towards 0,0
