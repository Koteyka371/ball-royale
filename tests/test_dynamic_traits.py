from ai.game_modes import GameMode
from arena.arena_types import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.dead_balls = []
        self.match_time = 0.0

class MockBall:
    def __init__(self, hp=100.0, speed=100.0, damage=10.0, traits=None, ball_type="easy"):
        self.id = 1
        self.alive = True
        self.max_hp = hp
        self.hp = hp
        self.base_speed = speed
        self.speed = speed
        self.base_damage = damage
        self.damage = damage
        self.traits = traits or []
        self.ball_type = ball_type
        self.team = "test"
        self.experience = 0
        self.level = 1

def test_dynamic_fire_trait():
    mode = GameMode()
    world = MockWorld()
    b = MockBall(traits=["fire"])

    # Needs to run mode.tick() to apply dynamic modifiers
    # First, test heatwave buff
    mode.weather = "heatwave"
    mode.tick(world, [b])

    assert b.speed == 120.0
    assert b.damage == 12.0

    # Then test rain debuff
    b.speed = b.base_speed
    b.damage = b.base_damage
    mode.weather = "rain"
    mode.tick(world, [b])

    assert b.speed == 80.0
    assert b.damage == 8.0

def test_dynamic_earth_trait():
    mode = GameMode()
    world = MockWorld()
    b = MockBall(traits=["earth"])

    # Test sandstorm immunity
    mode.weather = "sandstorm"
    b.weather_immunity_timer = 0.0
    mode.tick(world, [b], delta=0.5)

    # Should gain immunity matching delta
    assert getattr(b, "weather_immunity_timer", 0.0) >= 0.5

    # Test defense buff on dirt arena
    world.arena.name = "Dirt Arena"
    mode.tick(world, [b])

    assert getattr(b, "defense_multiplier", 1.0) == 0.8
