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
    import sys
    sys.modules["system.profile"] = type("Mock", (), {"ProfileManager": type("Mock", (), {"add_skill_points": lambda x: None})})
    import ai.game_modes as gm
    gm.ProfileManager = sys.modules["system.profile"].ProfileManager
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()
    balls = [MockBall(1), MockBall(2, "scout")]

    mode.setup(world, balls)
    assert hasattr(balls[0], "base_speed")

    # Tick with clear
    mode.weather = "clear"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == balls[0].base_speed

    # Tick with snow
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    assert balls[0].speed == balls[0].base_speed * 0.5
    assert balls[0].damage == balls[0].base_damage * 1.2

    # Tick with thunderstorm
    mode.weather = "thunderstorm"
    mode.tick(world, balls, 0.1)
    assert abs(balls[0].speed - (balls[0].base_speed * 1.1)) < 0.01
    assert balls[0].damage == balls[0].base_damage * 1.5

    # Tick with sandstorm
    mode.weather = "sandstorm"
    balls[0].hp = 100 # Reset HP
    mode.tick(world, balls, 0.1)
    assert abs(balls[0].speed - (balls[0].base_speed * 0.7)) < 0.01
    assert balls[0].damage == balls[0].base_damage
    mode.tick(world, balls, 0.9)
    assert balls[0].hp in [99.0, 79.0]
