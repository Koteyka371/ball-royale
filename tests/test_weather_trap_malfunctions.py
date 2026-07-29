from src.ai.action import Action
class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100
        self.speed = 100.0
        self.base_speed = 100.0
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.id = 999
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.trap_variant = "normal"
        self.owner_id = 998
        self.active = True
        self.duration = 5.0

class MockArena:
    def __init__(self, weather):
        self.weather = weather
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.game_mode = None
        self.events = []
        self.balls = []

def test_electric_beam_trap_rain_short_circuit():
    ball = MockBall(1, 0, 0)
    arena = MockArena("rain")
    world = MockWorld(arena)
    world.balls.append(ball)

    # Place electric beam directly on ball
    hazard = MockHazard("electric_beam_trap", 0, 0); hazard.damage = 10.0
    hazard.team = "enemy"
    arena.hazards.append(hazard)

    # Sanity check damage on clear weather
    arena.weather = "clear"
    ball.hp = 100
    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Should deal 2.0 damage per second => 0.2 damage
    assert ball.hp < 100

    # Test rain weather - should short circuit and deal NO damage
    arena.weather = "rain"
    ball.hp = 100
    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp == 100, "Electric beam trap should short circuit in rain and deal 0 damage"

def test_electric_bumper_rain_short_circuit():
    ball = MockBall(1, 0, 0)
    arena = MockArena("rain")
    world = MockWorld(arena)
    world.balls.append(ball)

    hazard = MockHazard("electric_bumper", 0, 0); hazard.damage = 10.0
    arena.hazards.append(hazard)

    arena.weather = "clear"
    ball.hp = 100
    ball.x = 0; ball.y = 0; hazard.x = 5; hazard.y = 0
    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp < 100

    arena.weather = "rain"
    ball.hp = 100
    ball.x = 0; ball.y = 0; hazard.x = 5; hazard.y = 0
    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.hp == 100
