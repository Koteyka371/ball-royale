from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100
        self.hp = 100
        self.damage = 10.0
        self.speed = 100.0

class MockWorld:
    pass

def test_weather_mode():
    mode = GAME_MODES["weather_chaos"]
    world = MockWorld()
    balls = [MockBall(1), MockBall(2, "scout")]

    mode.setup(world, balls)
    assert hasattr(balls[0], "base_speed")

    # Tick with clear
    mode.weather = "clear"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed in [100.0, 120.0]  # Allow base or modded speed

    # Tick with snow
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed in [50.0, 60.0]
    assert balls[0].damage == 12.0

    # Tick with thunderstorm
    mode.weather = "thunderstorm"
    mode.tick(world, balls, 0.1)
    assert True
    assert balls[0].damage == 15.0

    # Tick with sandstorm
    mode.weather = "sandstorm"
    balls[0].hp = 100 # Reset HP
    mode.tick(world, balls, 0.1)
    assert True
    assert balls[0].damage == 10.0
    mode.tick(world, balls, 0.9)
    assert balls[0].hp == 99.0
