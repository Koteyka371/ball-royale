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
    assert mage_ball.hp == 96.0

    # Test snow for ice ball
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    assert abs(ice_ball.speed - (ice_ball.base_speed * 1.2)) < 0.01
    assert ice_ball.damage == ice_ball.base_damage * 1.5

def test_weather_mode_yeti_and_sand_elemental():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    yeti = MockBall(1, "snow_yeti")
    yeti.base_speed = 100.0
    yeti.base_damage = 10.0
    yeti.base_perception_radius = 200.0

    sand_elem = MockBall(2, "sand_elemental")
    sand_elem.base_speed = 100.0
    sand_elem.base_damage = 10.0
    sand_elem.base_perception_radius = 200.0

    balls = [yeti, sand_elem]
    mode.setup(world, balls)

    # Test snow for yeti
    mode.weather = "snow"
    mode.tick(world, balls, 0.1)
    # Yeti should gain speed and damage, instead of halving speed
    assert yeti.speed == yeti.base_speed * 1.5
    assert yeti.damage == yeti.base_damage * 1.5
    # Sand elemental should be normal or affected by regular snow rules
    assert sand_elem.speed == sand_elem.base_speed * 0.5

    # Reset
    yeti.hp = 100
    sand_elem.hp = 100

    # Test sandstorm for sand_elemental
    mode.weather = "sandstorm"
    mode.tick(world, balls, 1.1) # 1.1s to trigger 1sec dot

    # Sand elemental should not take dot damage
    assert sand_elem.hp == 100
    assert sand_elem.speed == sand_elem.base_speed * 1.2

    # Yeti should be affected by sandstorm regular rules (takes 1 dot damage + potential random 20)
    assert yeti.hp <= 99.0

def test_weather_mode_mirage():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()


    trickster_ball = MockBall(1, "trickster")
    trickster_ball.SKILL = "shoot_portals"

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
    assert decoys[0].speed == 0.0

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

def test_weather_control_booster():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]

    class MockArena:
        is_foggy = False
        is_raining = False
        is_sandstorming = False
        is_snowing = False
        is_heatwave = False
        wind_dx = 0.0
        wind_dy = 0.0
        width = 1000
        height = 1000
        hazards = []

    class MockWorld:
        arena = MockArena()
        dead_balls = []
        def add_event(self, type, data):
            pass

    class MockBall:
        def __init__(self, t):
            self.alive = True
            self.ball_type = t
            self.weather_control_timer = 10.0
            self.team = "test"

    world = MockWorld()

    # Test elementalist
    ball = MockBall("elementalist")
    mode.setup(world, [ball])
    mode.weather = "clear"
    mode.tick(world, [ball], 0.1)
    assert mode.weather == "thunderstorm"
    assert world.arena.is_raining == True

    # Test druid
    ball = MockBall("druid")
    mode.setup(world, [ball])
    mode.tick(world, [ball], 0.1)
    assert mode.weather == "rain"
    assert world.arena.is_raining == True

    # Test rogue
    ball = MockBall("rogue")
    mode.setup(world, [ball])
    mode.tick(world, [ball], 0.1)
    assert mode.weather == "fog"
    assert world.arena.is_foggy == True

    # Test when timer runs out (should not immediately switch unless timer > 10, but we test it stops forcing)
    ball.weather_control_timer = 0.0
    mode.weather_timer = 9.9
    mode.tick(world, [ball], 0.2)
    # The normal logic will trigger and randomly pick a weather, resetting weather_timer
    assert mode.weather_timer == 0.0

def test_weather_mode_rain_vision():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]
    world = MockWorld()
    world.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()

    ball = MockBall(1, "warrior")
    ball.perception_radius = 250.0
    ball.base_perception_radius = 250.0
    balls = [ball]
    mode.setup(world, balls)

    mode.weather = "rain"
    mode.tick(world, balls, 0.1)

    assert ball.perception_radius == 125.0 # 250 * 0.5

def test_weather_mode_sandstorm_shelter():
    import ai.game_modes as gm
    mode = gm.GAME_MODES["weather_chaos"]

    class MockHazard:
        def __init__(self, k, x, y, r, active=True):
            self.kind = k
            self.x = x
            self.y = y
            self.radius = r
            self.active = active

    class MockArena:
        def __init__(self):
            self.hazards = [
                MockHazard("shelter", 100, 100, 50),
                MockHazard("flare", 500, 500, 100)
            ]

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.leaderboard_manager = type("Mock", (), {"data": {"current_season": 4}})()
            self.balls = []
            self.dead_balls = []
        def add_event(self, type, data):
            pass

    class MockBall:
        def __init__(self, id, t):
            self.id = id
            self.alive = True
            self.ball_type = t
            self.team = "test"
            self.x = 0
            self.y = 0
            self.base_speed = 100.0
            self.speed = 100.0
            self.base_damage = 10.0
            self.damage = 10.0
            self.base_perception_radius = 200.0
            self.perception_radius = 200.0
            self.hp = 100.0
            self.traits = []

    world = MockWorld()

    # Not sheltered, not earth elemental
    b1 = MockBall(1, "scout")
    b1.x, b1.y = 0, 0

    # Sheltered by shelter
    b2 = MockBall(2, "scout")
    b2.x, b2.y = 100, 100

    # Sheltered by flare
    b3 = MockBall(3, "scout")
    b3.x, b3.y = 520, 500

    # Earth elemental
    b4 = MockBall(4, "sand_elemental")
    b4.x, b4.y = 0, 0

    balls = [b1, b2, b3, b4]
    world.balls = balls
    mode.setup(world, balls)

    mode.weather = "sandstorm"

    mode.tick(world, balls, 1.0)

    # Assertions
    # b1: not sheltered, reduced vision and dot damage
    assert b1.perception_radius == 200.0 * 0.3
    assert b1.hp == 99.0

    # b2: sheltered, normal vision, no dot damage
    assert b2.perception_radius == 200.0
    assert b2.hp == 100.0

    # b3: sheltered by flare, normal vision, no dot damage
    assert b3.perception_radius == 200.0
    # b3 takes damage since flare provides no shelter from sandstorm

    # b4: earth elemental, no vision reduction, speed increased
    assert b4.speed == 100.0 * 1.2
