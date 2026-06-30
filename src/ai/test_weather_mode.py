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

def test_weather_mode_special_balls():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    mage_ball = MockBall(1, "mage")
    mage_ball.SKILL = "fireball"

    ice_ball = MockBall(2, "iceball_type")
    ice_ball.SKILL = "elemental_burst"

    balls = [mage_ball, ice_ball]
    mode.setup(world, balls)

    # Test rain for mage
    mode.weather = "rain"
    mode.tick(world, balls, 1.0)
    assert mage_ball.hp == 98.0  # 100 - 2.0 * 1.0

    # Test snow for ice ball
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    assert ice_ball.speed == ice_ball.base_speed * 1.2
    assert ice_ball.damage == ice_ball.base_damage * 1.5

def test_weather_mode_mirage():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()


    trickster_ball = MockBall(1, "trickster")
    trickster_ball.SKILL = "deploy_decoy"

    phantom_ball = MockBall(2, "phantom")
    phantom_ball.SKILL = "phase_through"

    balls = [trickster_ball, phantom_ball]
    world.balls = balls.copy()
    mode.setup(world, balls)

    # Test mirage in fog
    mode.weather = "fog"
    mode.tick(world, balls, 5.5)

    assert len(world.balls) > 2
    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) > 0
    assert getattr(decoys[0], 'is_decoy', False)

def test_weather_mode_heatwave():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()


    ball1 = MockBall(1, "warrior")
    ball2 = MockBall(2, "scout")

    balls = [ball1, ball2]
    world.balls = balls.copy()
    mode.setup(world, balls)

    mode.weather = "heatwave"
    # To test mirage we might need a mocked random inside mode
    old_rnd = getattr(mode, "random", None)
    import random
    mode.random = type("MockRandom", (), {"choice": random.choice, "uniform": lambda *args: 5.0, "random": lambda *args: 0.1, "randint": random.randint})()

    # Check speed reduction
    mode.tick(world, balls, 0.1)
    assert abs(ball1.speed - (ball1.base_speed * 0.9)) < 0.01

    # Check mirage spawn
    mode.tick(world, balls, 5.0)
    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) > 0

    mode.random = old_rnd
