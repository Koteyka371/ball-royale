import pytest
from ai.game_modes import GAME_MODES

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
    def __init__(self, x, y, hp=100, alive=True):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.max_hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.weather_immunity_timer = 0.0
        self.ball_type = "normal"
        self.team = "A"

def test_biome_safe_zones_mode():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()

    balls = [MockBall(500, 500)]

    mode.setup(world, balls)

    assert len(mode.zones) == 4
    for z in mode.zones:
        assert z["biome"] in mode.biomes

    # Manually place a zone right on the ball with "heal" biome
    mode.zones = [{
        "x": 500,
        "y": 500,
        "radius": 200,
        "target_x": 500,
        "target_y": 500,
        "biome": "heal"
    }]

    balls[0].hp = 50.0
    mode.tick(world, balls, 1.0)
    assert balls[0].hp == 60.0 # 50 + 10 * delta

    # Change to "speed"
    mode.zones[0]["biome"] = "speed"
    mode.tick(world, balls, 1.0)
    assert balls[0].speed >= 150.0
    assert getattr(balls[0], "biome_modifier_speed", False) == True

    # Ball moves outside
    balls[0].x = 1000
    balls[0].y = 1000
    mode.tick(world, balls, 1.0)
    assert balls[0].speed == balls[0].base_speed # speed restored
    assert not getattr(balls[0], "biome_modifier_speed", False)
    assert balls[0].hp < 60.0 # took storm damage
