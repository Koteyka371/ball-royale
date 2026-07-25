import pytest
from src.ai.action import Action
from src.ai.game_modes import GameMode

class MockBall:
    def __init__(self, x=0.0, y=0.0, id=1):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.radius = 10.0
        self.smokescreen_timer = 0.0
        self.fire_timer = 0.0

class MockHazard:
    def __init__(self, x, y, duration, max_duration):
        self.kind = "volcanic_fissure"
        self.x = x
        self.y = y
        self.radius = 100.0
        self.duration = duration
        self.max_duration = max_duration
        self.damage = 15.0
        self.owner_id = 999

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.game_mode = GameMode()

def test_volcanic_fissure_closed():
    ball = MockBall()
    world = MockWorld()
    world.balls = [ball]
    hazard = MockHazard(x=0.0, y=0.0, duration=9.0, max_duration=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute('', 1.0)

    assert ball.hp == 100.0
    assert ball.smokescreen_timer == 0.0
    assert ball.fire_timer == 0.0

def test_volcanic_fissure_open():
    ball = MockBall()
    world = MockWorld()
    world.balls = [ball]
    hazard = MockHazard(x=0.0, y=0.0, duration=5.0, max_duration=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute('', 1.0)

    assert ball.hp == 100.0 - 15.0
    assert ball.smokescreen_timer > 0.0
    assert ball.fire_timer > 0.0

def test_volcanic_fissure_out_of_range():
    ball = MockBall(x=200.0, y=200.0)
    world = MockWorld()
    world.balls = [ball]
    hazard = MockHazard(x=0.0, y=0.0, duration=5.0, max_duration=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute('', 1.0)

    assert ball.hp == 100.0
    assert ball.smokescreen_timer == 0.0
    assert ball.fire_timer == 0.0
