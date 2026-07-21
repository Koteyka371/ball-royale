import pytest
from ai.action import Action
from ai.game_modes import PinballMutatorMode

class MockBall:
    def __init__(self, id=1, team="A"):
        self.id = id
        self.team = team
        self.x = 5.0  # Near left wall
        self.y = 500.0
        self.vx = -100.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.hp = 100.0
        self.dash_cooldown = 10.0
        self.skill_cooldown = 10.0
        self.ball_type = "default"

class MockArena:
    def __init__(self):
        self.boundary_offsets = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
        self.boundary_states = {"left": "normal"}
        self.hazards = []
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, r):
        bounced = False
        if x < r: x, bounced = r, True
        return x, y, bounced

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.game_mode = PinballMutatorMode()
        self.balls = []
        self.mutators_active = True
        self.mutators = ["pinball_mutator"]

def test_pinball_mutator_movement():
    mode = PinballMutatorMode()
    ball = MockBall()
    ball.vx = 0.0
    ball.vy = 0.0
    mode.tick(MockWorld(), [ball], 0.016)

    speed_sq = ball.vx**2 + ball.vy**2
    assert speed_sq > 250000.0, "Ball should be forced to move fast"

def test_pinball_mutator_wall_bounce():
    world = MockWorld()
    ball = MockBall()
    ball.vx = -2000.0 # High speed towards left wall
    world.balls.append(ball)

    action = Action(ball, world)
    bounced_wall = action._clamp_position()
    assert bounced_wall == True

    # Manually trigger bounce logic from execute if needed, or we just execute it
    # execute does _clamp_position and then applies bounce logic
    # Reset position so execute can do it
    ball.x = 5.0
    ball.vx = -2000.0

    initial_hp = ball.hp
    action.execute("idle", 0.016)

    # Check if damage was avoided
    assert ball.hp == initial_hp, "Ball should not take wall damage in Pinball Mutator"

    # Check massive momentum
    assert ball.vx > 2000.0, "Speed should be massively boosted"

    # Check cooldowns
    assert ball.dash_cooldown == 0.0, "Dash cooldown should be reset"
    assert ball.skill_cooldown == 0.0, "Skill cooldown should be reset"
