import pytest
import math

class MockBall:
    def __init__(self, id, ball_type="easy"):
        self.id = id
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.mass = 1.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "A"
        self.ball_type = ball_type
        self.status_effects = {}
        self.is_stunned = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.game_mode = None
        self.width = 1000
        self.height = 1000
        # Make clamp_position return True for bounced to trigger the block
        self.arena = type('MockArena', (), {'clamp_position': lambda self, x, y, r: (x, 15.0, True), 'boundary_states': {}})()
        self.leaderboard_manager = type('MockLBM', (), {'data': {'current_season': 1}})()

def test_super_bouncy_walls_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get("super_bouncy_walls")
    assert mode is not None, "SuperBouncyWallsMode should be registered in GAME_MODES"
    assert mode.name == "Super Bouncy Walls"

    from ai.action import Action
    world = MockWorld()
    world.game_mode = mode
    ball = MockBall(1)

    ball.x = 500
    ball.y = 5
    ball.vx = 0
    ball.vy = -500

    world.balls.append(ball)

    action = Action(ball, world)

    action.execute(strategy='idle', delta=0.1)

    expected_speed = 500.0 * 4.0

    actual_speed = math.sqrt(ball.vx**2 + ball.vy**2)

    assert abs(actual_speed - expected_speed) < 10.0, f"Expected speed ~{expected_speed}, got {actual_speed}"
