import sys
sys.path.insert(0, 'src')
from ai.game_modes import MeteorBombardmentMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0

    def take_damage(self, amount):
        self.hp -= amount

def test_meteor_bombardment():
    import random
    random.seed(42)
    mode = MeteorBombardmentMode()
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode.setup(world, balls)

    mode.bombard_timer = 9.9
    mode.tick(world, balls, delta=0.2)

    assert len(mode.active_meteors) >= 5
    assert len(mode.active_meteors) <= 10

    # Place ball far away
    balls[0].x = -1000
    balls[0].y = -1000

    # Fast forward meteor delay
    mode.tick(world, balls, delta=2.8)

    assert len(mode.craters) >= 5
    assert balls[0].hp == 100.0

    # Move ball into crater
    crater = mode.craters[0]
    balls[0].x = crater["x"]
    balls[0].y = crater["y"]

    # Tick to take crater damage (20 * 1.0)
    mode.tick(world, balls, delta=1.0)
    assert abs(balls[0].hp - 80.0) < 0.001
