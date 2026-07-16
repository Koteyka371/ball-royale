import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.flip_timer = 0.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 200 # 200 * 0.016 = 3.2 seconds
        self.events = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_flipper_trigger = 0.0

def test_trigger_flipper():
    world = MockWorld()
    flipper = MockHazard("pinball_flipper", 100.0, 100.0)
    world.arena.hazards.append(flipper)

    ball = MockBall(150.0, 150.0)

    action = Action(ball, world)
    action.execute("trigger_flipper", 0.016)

    assert flipper.flip_timer == 0.5
    assert ball.last_flipper_trigger == 3.2

    # Test cooldown
    world.tick = 205 # 205 * 0.016 = 3.28 (diff is 0.08 < 2.0)
    flipper.flip_timer = 0.0
    action.execute("trigger_flipper", 0.016)

    assert flipper.flip_timer == 0.0
