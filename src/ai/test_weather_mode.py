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
        self.x = 50.0
        self.y = 50.0
        self.vx = 10.0
        self.vy = 10.0

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
    assert balls[0].speed == 100.0

    # Tick with snow
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == 50.0
    assert balls[0].damage == 12.0

    # Tick with thunderstorm
    mode.weather = "thunderstorm"
    mode.tick(world, balls, 0.1)
    assert abs(balls[0].speed - 110.0) < 0.01
    assert balls[0].damage == 15.0

    # Tick with sandstorm
    mode.weather = "sandstorm"
    balls[0].hp = 100 # Reset HP
    mode.tick(world, balls, 0.1)
    assert abs(balls[0].speed - 70.0) < 0.01
    assert balls[0].damage == 10.0
    mode.tick(world, balls, 0.9)
    assert abs(balls[0].hp - 99.0) < 0.1 or abs(balls[0].hp - 79.0) < 0.1

    # Tick with hurricane
    mode.weather = "hurricane"
    balls[0].x = 400.0
    balls[0].y = 400.0
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == 90.0
    assert balls[0].dash_range_mult == 1.0
    assert balls[0].steering_mult == 0.5
    assert balls[0].x != 400.0
    assert balls[0].y != 400.0

    # Tick with earthquake
    mode.weather = "earthquake"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == 40.0
    assert balls[0].dash_range_mult == 0.1
    assert balls[0].steering_mult == 0.1

    # Tick with icy
    mode.weather = "icy"
    old_x = balls[0].x
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == 60.0
    assert balls[0].dash_range_mult == 2.0
    assert balls[0].steering_mult == 0.1
    assert balls[0].x != old_x
