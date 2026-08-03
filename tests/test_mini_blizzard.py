import pytest
from ai.game_modes import TornadoSwarmEventMode
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id=1, x=100.0, y=100.0, team="TeamA", ball_type="default"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.speed_mult = 1.0
        self.radius = 10.0
        self.is_frozen = False
        self.freeze_stack = 0.0
        self.frozen_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.game_mode = None

def test_mini_blizzard_creation():
    mode = TornadoSwarmEventMode()
    world = MockWorld()

    # Setup initial hazards: one mini_tornado and one ice_patch close to each other
    tornado = Hazard(id=1, x=100.0, y=100.0, radius=30.0, kind="mini_tornado", damage=15.0)
    tornado.vx = 0.0
    tornado.vy = 0.0

    ice = Hazard(id=2, x=110.0, y=110.0, radius=50.0, kind="ice_patch", damage=0.0)

    world.arena.hazards = [tornado, ice]

    # Tick the mode
    mode.tick(world, [], delta=0.016)

    # The tornado should have been converted into a mini_blizzard
    assert tornado.kind == "mini_blizzard"
    assert tornado.damage == 10.0

def test_mini_blizzard_effect():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0)
    world.balls.append(ball)

    hazard = Hazard(id=1, x=100.0, y=100.0, radius=30.0, kind="mini_blizzard", damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Initial state
    assert ball.speed_mult == 1.0
    assert ball.freeze_stack == 0.0

    # Execute action to apply hazard effects
    action.execute("default", 0.016)

    # Assert effects
    assert ball.speed_mult < 1.0  # Should be multiplied by 0.3
    assert ball.freeze_stack > 0.0  # Should accumulate freeze stack
    assert ball.hp < 100.0  # Should take damage

    # Force freeze stack to near 100
    ball.freeze_stack = 99.0
    action.execute("default", 0.1) # Execute with larger delta to cross 100 threshold

    # Assert frozen
    assert ball.frozen_timer > 0.0
    assert ball.freeze_stack == 0.0 # Should reset
