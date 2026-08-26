from ai.game_modes import AbyssalFogEventMode

class MockBall:
    def __init__(self):
        self.base_perception_radius = 500.0
        self.perception_radius = 500.0
        self.vision_radius = 500.0

    def set_meta(self, key, value):
        setattr(self, key, value)

    def get_meta(self, key):
        return getattr(self, key)

    def has_meta(self, key):
        return hasattr(self, key)

    def has_method(self, name):
        return hasattr(self, name) and callable(getattr(self, name))

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_abyssal_fog_event():
    mode = AbyssalFogEventMode()
    ball = MockBall()
    world = MockWorld()
    mode.setup(world, [ball])

    assert mode.fog_active

    # Tick 1 second, verify radius drops to 150
    mode.tick(world, [ball], 1.0)
    assert ball.perception_radius == 150.0
    assert ball.vision_radius == 150.0

    # Tick remaining 14 seconds (15 - 1), verify radius is restored
    mode.tick(world, [ball], 14.0)
    assert not mode.fog_active
    assert ball.perception_radius == 500.0
    assert ball.vision_radius == 500.0
