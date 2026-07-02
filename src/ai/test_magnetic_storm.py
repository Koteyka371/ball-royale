from ai.game_modes import GAME_MODES
import math

class MockBall:
    def __init__(self, id, x=0, y=0, ball_type="warrior", alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100
        self.hp = 100
        self.damage = 10.0
        self.speed = 100.0

class MockWorld:
    pass

def test_magnetic_storm_attract():
    mode = GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 100, 0)
    b1.polarity = 1
    b2.polarity = -1

    balls = [b1, b2]
    world.balls = balls
    mode.setup(world, balls)

    mode.weather = "magnetic_storm"
    mode.tick(world, balls, 0.1)

    assert b1.x > 0 # b1 pulled towards b2
    assert b2.x < 100 # b2 pulled towards b1
    assert b1.cosmetic == "magnet_plus"
    assert b2.cosmetic == "magnet_minus"

def test_magnetic_storm_repel():
    mode = GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 100, 0)
    b1.polarity = 1
    b2.polarity = 1

    balls = [b1, b2]
    world.balls = balls
    mode.setup(world, balls)

    mode.weather = "magnetic_storm"
    mode.tick(world, balls, 0.1)

    assert b1.x < 0 # b1 pushed away from b2
    assert b2.x > 100 # b2 pushed away from b1
    assert b1.cosmetic == "magnet_plus"
    assert b2.cosmetic == "magnet_plus"

def test_magnetic_storm_assigns_polarity():
    mode = GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    b1 = MockBall(1, 0, 0)
    balls = [b1]
    world.balls = balls
    mode.setup(world, balls)

    mode.weather = "magnetic_storm"
    mode.tick(world, balls, 0.1)

    assert hasattr(b1, "polarity")
    assert b1.polarity in [1, -1]
    assert b1.cosmetic in ["magnet_plus", "magnet_minus"]
