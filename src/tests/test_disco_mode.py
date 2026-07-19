import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, speed=100.0, stamina=100.0, max_stamina=100.0, hp=100.0):
        self.alive = True
        self.ball_type = "test"
        self.x = x
        self.y = y
        self.radius = 15.0
        self.base_speed = speed
        self.speed = speed
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.hp = hp
        self.max_hp = 100.0
        self.killer = None
        self.weather_immunity_timer = 0.0
        self.traits = []

class MockHazard:
    def __init__(self, kind, x, y, radius, color):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.weather = "clear"
        self.name = "default"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.weekly_mutator = ""
        self.mutators_active = False
        self.mutators = []

def test_disco_floor_mode():
    mode = GAME_MODES.get("disco_floor")
    assert mode is not None

    world = MockWorld()
    balls = [
        MockBall(x=500, y=500, speed=100, stamina=50, hp=100),
        MockBall(x=800, y=800, speed=100, stamina=50, hp=100)
    ]

    import ai.game_modes as gm
    original_tick = gm.GameMode.tick
    gm.GameMode.tick = lambda self, w, b, d: None

    mode.setup(world, balls)

    p1 = MockHazard("disco_panel", 500, 500, 150.0, "red")
    p2 = MockHazard("disco_panel", 800, 800, 150.0, "blue")
    world.arena.hazards = [p1, p2]

    mode.current_color = "red"
    mode.beat_interval = 2.0
    mode.rhythm_timer = 0.0

    mode.tick(world, balls, delta=1.0)

    assert abs(balls[0].speed - 150.0) < 0.1 or abs(balls[0].speed - 180.0) < 0.1
    assert abs(balls[0].stamina - 70.0) < 0.1
    assert abs(balls[0].hp - 100.0) < 0.1

    assert abs(balls[1].speed - 50.0) < 0.1 or abs(balls[1].speed - 60.0) < 0.1
    assert abs(balls[1].stamina - 50.0) < 0.1
    assert abs(balls[1].hp - 80.0) < 0.1

    mode.current_color = "blue"
    mode.tick(world, balls, delta=0.2)

    assert abs(balls[0].speed - 50.0) < 0.1 or abs(balls[0].speed - 60.0) < 0.1
    assert abs(balls[0].hp - (100.0 - 20.0 * 0.2)) < 0.1

    assert abs(balls[1].speed - 150.0) < 0.1 or abs(balls[1].speed - 180.0) < 0.1
    assert abs(balls[1].stamina - (50.0 + 20.0 * 0.2)) < 0.1

    gm.GameMode.tick = original_tick
