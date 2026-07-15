import pytest

class MockWorld:
    def __init__(self):
        self.events = []
        self.boosters = []
        class MockArena:
            def __init__(self):
                self.width = 1000
                self.height = 1000
                self.hazards = []
                self.items = []
        self.arena = MockArena()
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, **kwargs):
        self.alive = True
        self.base_damage = 10.0
        self.damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_max_hp = 100.0
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_acid_rain_effects():
    from ai.game_modes import ExtremeWeatherMode
    mode = ExtremeWeatherMode()
    world = MockWorld()

    # Metal ball (should take armor damage)
    b1 = MockBall(ball_type="metal_drone", hp=100.0, max_hp=100.0)

    # Non-metal ball (should take normal damage based on current implementation)
    b2 = MockBall(ball_type="basic", hp=100.0, max_hp=100.0)

    # Ball with hazmat suit (should be immune)
    b3 = MockBall(ball_type="metal_drone", hp=100.0, max_hp=100.0, hazmat_booster_timer=10.0)

    balls = [b1, b2, b3]
    mode.setup(world, balls)
    mode.current_weather = "acid_rain"

    # Execute one tick of 1.0 seconds
    mode.tick(world, balls, 1.0)

    print(f"b1 HP: {b1.hp}, Max HP: {b1.max_hp}, Damage: {b1.damage}")
    print(f"b2 HP: {b2.hp}, Max HP: {b2.max_hp}, Damage: {b2.damage}")
    print(f"b3 HP: {b3.hp}, Max HP: {b3.max_hp}, Damage: {b3.damage}")

test_acid_rain_effects()
