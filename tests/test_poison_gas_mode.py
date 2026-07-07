import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "test"
        self.hp = 100
        self.team = "test"
        self.poison_timer = 0.0

def test_poison_gas_mode_logic():
    mode = GAME_MODES["poison_gas_zone"]
    world = MockWorld()

    # 500,500 is center. We place ball way out at 10,10 to be out of the 500 zone
    balls = [MockBall(10, 10), MockBall(500, 500)]

    mode.setup(world, balls)

    # Tick loop to exceed 0.5s for the visual event
    for _ in range(60):
        mode.tick(world, balls, delta=0.016)

    assert mode.zone_radius < 500.0 # Shrinking

    # Ball 1 (outside) should take severe damage and gain poison_timer
    assert balls[0].hp < 100
    assert balls[0].poison_timer > 0.0

    # Ball 2 (inside) should be fine and no poison
    assert balls[1].hp == 100
    assert balls[1].poison_timer == 0.0

    # Event added
    ambient_events = [e for e in world.events if e[0] == "poison_gas_ambient"]
    assert len(ambient_events) > 0
