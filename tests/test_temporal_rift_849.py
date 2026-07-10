import math
from ai.game_modes import TemporalRiftMode
from ai.action import Action
from ai.game_modes import GAME_MODES

class Hazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.arena_width = 1000
        self.arena_height = 1000
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.dead_balls = []

    def get_nearby_entities(self, ball, radius):
        return {"boosters": [], "hazards": [], "enemies": []}

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed_multiplier = 1.0
        self.alive = True
        self.team = "test"
        self.ball_type = "easy"

def test_temporal_rift_effect_slow():
    world = MockWorld()
    ball = MockBall(1, 500, 500)

    # Pre-action speed multipliers
    ball.speed_multiplier = 1.0
    ball.vx = 100.0
    ball.vy = 100.0

    # Spawn a slow rift
    rift = Hazard("rift_1", 500, 500, 200, "slow_rift", 0.0)
    world.arena.hazards.append(rift)

    action = Action(ball, world)
    try:
        action.execute("wander", 1.0)
    except Exception as e:
        pass

    assert ball.speed_multiplier <= 0.2

def test_temporal_rift_effect_fast():
    world = MockWorld()
    ball = MockBall(2, 500, 500)

    # Pre-action speed multipliers
    ball.speed_multiplier = 1.0
    ball.vx = 100.0
    ball.vy = 100.0

    # Spawn a fast rift
    rift = Hazard("rift_2", 500, 500, 200, "fast_rift", 0.0)
    world.arena.hazards.append(rift)

    action = Action(ball, world)
    try:
        action.execute("wander", 1.0)
    except Exception as e:
        pass

    assert ball.speed_multiplier >= 2.5

def test_temporal_rift_game_mode():
    mode = GAME_MODES["temporal_rift"]
    world = MockWorld()
    mode.setup(world, [])

    assert mode.rift_spawn_timer == 5.0

    # Tick to trigger spawn
    mode.tick(world, [], 5.1)

    assert len(world.arena.hazards) > 0
    rift = world.arena.hazards[0]
    assert rift.kind in ["slow_rift", "fast_rift"]
