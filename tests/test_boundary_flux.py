import pytest
from src.ai.action import Action
from src.ai.game_modes import BoundaryFluxMode

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0
        self.y = 500
        self.vx = -100
        self.vy = 0
        self.radius = 10
        self.team = "players"
        self.hp = 100
        self.speed = 100
        self.base_speed = 100
        self.ball_type = "easy"
        self.is_flying = False
        self.current_action = "none"
        self.perception_radius = 500
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0
        self.is_frictionless = False

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.game_mode = BoundaryFluxMode()

    def get_nearby_entities(self, ball, dist):
        return {"enemies": [], "allies": []}

def test_boundary_flux_mode():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    action = Action(ball, world)
    action._process_physics = lambda d: None
    action._clamp_position = lambda: True
    action._idle = lambda d: None
    action._chase = lambda d: None
    action._flee = lambda d: None

    # Pattern 0: horizontal hit bouncy, vertical hit sticky
    world.game_mode.current_pattern = 0

    # Hit left wall (x <= margin), this is hit_vertical
    ball.x = 0
    ball.y = 500
    ball.vx = -100
    ball.vy = 0

    action.execute("none", 1.0)

    # Vertical wall on pattern 0 is sticky -> velocity should be 0
    assert abs(ball.vx) < 150
    assert abs(ball.vy) < 150

    # Hit top wall (y <= margin), this is hit_horizontal
    ball.x = 500
    ball.y = 0
    ball.vx = 0
    ball.vy = -100

    # Reset some knockback states that might cause damage calculations
    ball._knockback_timer = 0

    action.execute("none", 1.0)

    # Horizontal wall on pattern 0 is bouncy -> velocity should reflect and increase speed
    assert ball.vy > 0 # vy should be positive now
    speed = (ball.vx**2 + ball.vy**2)**0.5
    assert speed > 150 # original speed was 100, bouncy multiplies by 2 (capped at 3000), so 200 > 150

    # Change pattern
    world.game_mode.current_pattern = 1

    # Hit left wall again, should be bouncy now
    ball.x = 0
    ball.y = 500
    ball.vx = -100
    ball.vy = 0

    action.execute("none", 1.0)
    assert ball.vx > 0

    # Hit top wall again, should be sticky now
    ball.x = 500
    ball.y = 0
    ball.vx = 0
    ball.vy = -100

    action.execute("none", 1.0)
    assert abs(ball.vx) < 150
    assert abs(ball.vy) < 150
