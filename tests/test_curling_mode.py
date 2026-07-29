import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.base_friction = 1.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val, team, x, y, ball_type="normal"):
        self.id = id_val
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = ball_type
        self.friction_multiplier = 1.0
        self.is_frictionless = False

def test_curling_mode_setup_and_tick():
    assert "curling" in GAME_MODES
    mode = GAME_MODES["curling"]
    mode.timer = 15.0 # reset just in case

    world = MockWorld()
    ball1 = MockBall(1, "Team A", 100, 100)
    balls = [ball1]

    # Setup
    mode.setup(world, balls)

    # Assert arena friction and target marker
    assert world.arena.base_friction == 0.05
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "target_marker"
    assert world.arena.hazards[0].x == 500.0
    assert world.arena.hazards[0].y == 500.0

    # Assert initial ball state
    assert ball1.friction_multiplier == 0.05

    # Tick
    mode.tick(world, balls, delta=1.0)
    assert mode.timer == 14.0
    assert ball1.friction_multiplier == 0.05
    assert ball1.is_frictionless == True

def test_curling_mode_winner():
    mode = GAME_MODES["curling"]
    mode.target_x = 500.0
    mode.target_y = 500.0

    world = MockWorld()

    # Ball 1 is at 400, 500 (distance 100)
    ball1 = MockBall(1, "Team A", 400, 500)
    # Ball 2 is at 520, 500 (distance 20) -> Closest!
    ball2 = MockBall(2, "Team B", 520, 500)
    # Ball 3 is a spectator (should be ignored) at 500, 500 (distance 0)
    ball3 = MockBall(3, "SpectatorTeam", 500, 500, "spectator")

    balls = [ball1, ball2, ball3]

    # Timer not expired
    mode.timer = 5.0
    assert mode.check_winner(world, balls) is None

    # Timer expired
    mode.timer = 0.0
    winner = mode.check_winner(world, balls)

    assert winner == "Team B"
