
import sys
sys.path.insert(0, 'src')
from ai.game_modes import ExplosiveMeteorsMode
import math

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
        self.hp = 200.0
        self.ball_type = "basic"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 500.0
        self.invisible = False

    def take_damage(self, amount):
        self.hp -= amount

def test_explosive_meteors():
    import random
    random.seed(42)
    mode = ExplosiveMeteorsMode()
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode.setup(world, balls)

    assert len(mode.active_meteors) == 0

    # Tick below spawn timer
    mode.tick(world, balls, delta=1.5)
    assert len(mode.active_meteors) == 0

    # Tick above spawn timer
    mode.tick(world, balls, delta=0.6)
    assert len(mode.active_meteors) == 1

    # Move ball right under meteor
    meteor = mode.active_meteors[0]
    balls[0].x = meteor["x"]
    balls[0].y = meteor["y"]

    # Fast forward so meteor explodes
    # Since timer is reset after spawn, spawn_timer is 0.1 at this point.
    # 2.0s tick will explode the meteor (delay=2.0) and spawn a new one (timer = 2.1 >= 2.0).
    # Oh wait! In game_modes.py, the tick loop checks spawn_timer first.
    # Let's just tick in small increments
    for _ in range(21):
        mode.tick(world, balls, delta=0.1)

    # Check HP drop
    assert balls[0].hp == 100.0
