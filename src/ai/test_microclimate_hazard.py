import pytest
from ai.game_modes import GAME_MODES, MicroclimateHazardMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.events = []
    def _deal_damage(self, attacker, target, amount):
        target.hp -= amount

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"

def test_microclimate_hazard_setup():
    mode = MicroclimateHazardMode()
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 3
    for h in world.arena.hazards:
        assert h.kind == "microclimate"
        assert h.weather == "heatwave"
        assert getattr(h, "vx", None) is not None

def test_microclimate_hazard_flip_and_effects():
    mode = MicroclimateHazardMode()
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    mode.setup(world, balls)

    # reset base_speed since some other setup might have changed it
    balls[0].base_speed = 100.0
    balls[0].speed = 100.0

    # ensure it stays in place
    hazard = world.arena.hazards[0]
    hazard.x = 500
    hazard.y = 500
    hazard.vx = 0
    hazard.vy = 0
    hazard.weather = "heatwave"

    # Test heatwave
    mode.tick(world, balls, delta=1.0)
    assert balls[0].hp < 100.0, f"hp: {balls[0].hp}"

    # Test flip to blizzard
    mode.weather_timer = 4.0
    mode.tick(world, balls, delta=1.0)
    assert hazard.weather == "blizzard", f"weather: {hazard.weather}"
    assert balls[0].speed <= 40.0, f"speed: {balls[0].speed}, base_speed: {balls[0].base_speed}"
