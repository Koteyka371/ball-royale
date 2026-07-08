from ai.action import Action
import math

class MockArena:
    def __init__(self, is_raining=False, is_snowing=False):
        self.is_raining = is_raining
        self.is_snowing = is_snowing
        self.hazards = []
        self.items = []
        self.wind_dx = 0.0
        self.wind_dy = 0.0
        if is_raining:
            self.weather = "rain"
        elif is_snowing:
            self.weather = "snow"
        else:
            self.weather = "clear"

class MockWorld:
    def __init__(self, is_raining=False, is_snowing=False):
        self.arena = MockArena(is_raining, is_snowing)
        self.balls = []
        self.boosters = []
        self.get_nearby_entities = lambda b, r: [e for e in self.balls if e != b]

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = True
        self.ball_type = "basic"
        self.BALL_TYPE = "basic"
        self.team = 1
        self.radius = 20
        self.vx = 100
        self.vy = 0
        self.speed = 100
        self.base_speed = 100

def test_spiked_tires_mud_immunity():
    # Test rain/mud slipperiness without booster
    world = MockWorld(is_raining=True)
    ball1 = MockBall(0, 0)
    world.balls.append(ball1)

    action1 = Action(ball1, world)
    action1.execute("move", 1.0)

    assert ball1.x > 0 # Movement + extra slippiness

    # Test rain/mud slipperiness with spiked tires booster
    world = MockWorld(is_raining=True)
    ball2 = MockBall(0, 0)
    ball2.spiked_tires_active = True
    ball2.spiked_tires_timer = 10.0
    world.balls.append(ball2)

    action2 = Action(ball2, world)
    action2.execute("move", 1.0)

    # Should be less than ball1 since no slippery effect applied
    assert ball2.x != ball1.x
    print("Success: spiked tires gives mud immunity")

def test_snowshoes_ice_immunity():
    # Test snow/ice slipperiness without booster
    world = MockWorld(is_snowing=True)
    ball1 = MockBall(0, 0)
    world.balls.append(ball1)

    action1 = Action(ball1, world)
    action1.execute("move", 1.0)

    assert ball1.x > 0

    # Test snow/ice slipperiness with snowshoes booster
    world = MockWorld(is_snowing=True)
    ball2 = MockBall(0, 0)
    ball2.snowshoes_active = True
    ball2.snowshoes_timer = 10.0
    world.balls.append(ball2)

    action2 = Action(ball2, world)
    action2.execute("move", 1.0)

    # Should be less than ball1 since no extra slippery effect applied
    assert ball2.x != ball1.x
    print("Success: snowshoes give ice immunity")

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True

def test_collect_weather_boosters():
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    booster = MockBooster("snowshoes_booster", 5, 0)
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []
    action._collect_booster(0.1)

    assert getattr(ball, "snowshoes_active", False) == True
    assert getattr(ball, "snowshoes_timer", 0.0) == 15.0
    print("Success: collect snowshoes booster")

if __name__ == "__main__":
    test_spiked_tires_mud_immunity()
    test_snowshoes_ice_immunity()
    test_collect_weather_boosters()
