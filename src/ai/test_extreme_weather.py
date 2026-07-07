import pytest

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "test_custom_type"
        self.x = 500
        self.y = 500
        self.speed = 100.0
        self.damage = 10.0
        self.hp = 100.0
        self.is_decoy = False

    def take_damage(self, amount):
        self.hp -= amount

def test_extreme_weather_mode_setup_and_tick():
    from ai.game_modes import ExtremeWeatherMode

    mode = ExtremeWeatherMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall()
    balls = [b1, b2]

    mode.setup(world, balls)

    assert hasattr(b1, "base_speed")
    assert b1.base_speed > 0

    # Tick for 15s to trigger weather change
    mode.tick(world, balls, 15.0)

    assert mode.current_weather in ["blizzard", "heatwave", "acid_rain", "hurricane", "tsunami"]
    assert len(world.boosters) == 2 # 2 balls, 1 booster each spawned

    kind = world.boosters[0].kind
    expected = {
        "blizzard": "thermal_booster",
        "heatwave": "cooling_booster",
        "acid_rain": "hazmat_booster",
        "hurricane": "heavy_anchor_booster",
        "tsunami": "life_jacket_booster"
    }[mode.current_weather]
    assert kind == expected

def test_extreme_weather_mode_effects():
    from ai.game_modes import ExtremeWeatherMode

    mode = ExtremeWeatherMode()
    world = MockWorld()
    b1 = MockBall() # Without booster
    b2 = MockBall() # With booster
    balls = [b1, b2]

    mode.setup(world, balls)

    mode.current_weather = "blizzard"
    b2.thermal_booster_timer = 10.0
    mode.tick(world, balls, 1.0)

    # b1 punished
    assert b1.speed == b1.base_speed * 0.2
    assert b1.hp < 100.0

    # b2 protected
    assert b2.speed == b2.base_speed
    assert b2.hp == 100.0

    # Test heatwave
    mode.current_weather = "heatwave"
    b1.hp = 100.0
    b2.hp = 100.0
    b2.cooling_booster_timer = 10.0

    mode.tick(world, balls, 1.0)
    assert b1.hp < 100.0
    assert b2.hp == 100.0

    # Test tsunami
    mode.current_weather = "tsunami"
    b1.x = 500
    b1.hp = 100.0
    b2.x = 500
    b2.hp = 100.0
    b2.life_jacket_booster_timer = 10.0

    mode.tick(world, balls, 1.0)
    assert b1.x == 800.0 # 500 + 300 * 1.0
    assert b2.x == 500.0 # b2 is protected

    # Test wall hit damage
    b1.x = 980
    b1.hp = 100.0
    mode.tick(world, balls, 1.0)
    assert b1.hp == 80.0 # 100 - 20 * 1.0
    assert b1.x == 1280.0
