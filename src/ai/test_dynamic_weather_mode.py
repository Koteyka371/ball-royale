from game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x=0.0, y=0.0, hp=100, ball_type="warrior", alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.ball_type = ball_type
        self.alive = alive

class MockWorld:
    pass

def test_dynamic_weather_mode_physics():
    mode = GAME_MODES["dynamic_weather"]
    world = MockWorld()

    ball = MockBall(1, 100.0, 100.0)
    balls = [ball]

    # Test Wind
    mode.current_weather = "wind"
    mode.wind_dir = (1.0, 0.0)
    mode.tick(world, balls, delta=1.0) # Apply 1s of wind
    assert ball.x > 100.0 # Should be pushed right by wind

    # Test Storm damage and push
    mode.current_weather = "storm"
    mode.wind_dir = (1.0, 0.0)
    import random
    random.seed(42) # Try to get damage
    for _ in range(1000): # Force some ticks to trigger the 1% chance
        mode.tick(world, balls, delta=0.016)

    assert ball.hp < 100 # Should have taken some damage from lightning

    # Test Rain
    ball_start_x = ball.x
    mode.current_weather = "rain"
    mode.tick(world, balls, delta=1.0)
    # Just verify it doesn't crash and slightly moves
    assert ball.x != ball_start_x or ball.y != 100.0
