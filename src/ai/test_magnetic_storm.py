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

def test_magnetic_storm_chain_damage():
    from ai.action import Action

    class MockWorldChain:
        def __init__(self):
            self.arena = None
            self.balls = []
            self.game_mode = type('GameMode', (), {'weather': 'magnetic_storm'})()

        def _deal_damage(self, attacker, target):
            if hasattr(target, "hp"):
                target.hp -= getattr(attacker, "damage", 10.0)

    class MockBallChain:
        def __init__(self, id, x, y, hp=100.0, team="A", ball_type="basic"):
            self.id = id
            self.x = x
            self.y = y
            self.hp = hp
            self.team = team
            self.ball_type = ball_type
            self.alive = True
            self.damage = 20.0

    world = MockWorldChain()
    b1 = MockBallChain(1, 100, 100, team="A")
    b2 = MockBallChain(2, 120, 100, team="B")
    b3 = MockBallChain(3, 140, 100, team="B")

    world.balls = [b1, b2, b3]

    # Force chain randomness to be 100%
    import random
    original_random = random.random
    random.random = lambda: 0.0

    try:
        action = Action(b1, world)
        action._attempt_damage(b1, b2)

        # Original damage 20
        # Chain damage 10
        assert b2.hp == 80.0
        assert b3.hp == 90.0
    finally:
        random.random = original_random
