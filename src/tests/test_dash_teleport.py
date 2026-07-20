import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

    def clamp_position(self, x, y, radius):
        bounced = False
        new_x = x
        new_y = y

        if x < radius:
            new_x = radius
            bounced = True
        elif x > self.width - radius:
            new_x = self.width - radius
            bounced = True

        if y < radius:
            new_y = radius
            bounced = True
        elif y > self.height - radius:
            new_y = self.height - radius
            bounced = True

        return new_x, new_y, bounced

class MockGameMode:
    pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.game_mode = MockGameMode()
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": [], "boosters": []}

class MockBall:
    def __init__(self, x, y, vx, vy, skill="dash"):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.skill = skill
        self.skill_timer = 0.0
        self.dash_range_mult = 1.0
        self.alive = True
        self.hp = 100.0
        self.team = "A"

def test_dash_teleport():
    # Place ball near right wall (x=990), with 10 radius.
    # The wall is at 1000, max x is 990.
    # Ball is at x=950, dashing perfectly right -> distance 100.
    # It should hit the wall at x=990, teleporting directly.
    ball = MockBall(950.0, 500.0, 10.0, 0.0)

    # We add a fake enemy perfectly right to force direction
    enemy = MockBall(2000.0, 500.0, 0.0, 0.0)
    enemy.team = "B"

    world = MockWorld()
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Fake get_enemies to return the enemy
    action._get_enemies = lambda: [enemy]

    # Manually trigger the dash
    action._use_skill()

    # Check if ball teleported and stopped at the wall correctly
    assert abs(ball.x - 990.0) < 1.0, f"Expected ball x to be 990, but got {ball.x}"
    assert ball.y == 500.0

    # Check quantum state and decoy
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "intangible_timer", 0.0) == 0.5

    # Assert a decoy was left behind
    assert len(world.balls) == 3
    decoy = world.balls[-1]
    assert getattr(decoy, "decoy_type", "") == "dash_decoy"
    assert decoy.x == 950.0
    assert decoy.y == 500.0

    # Check quantum state and decoy
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "intangible_timer", 0.0) == 0.5

    # Assert a decoy was left behind
    assert len(world.balls) == 3
    decoy = world.balls[-1]
    assert getattr(decoy, "decoy_type", "") == "dash_decoy"
    assert decoy.x == 950.0
    assert decoy.y == 500.0

    # Check quantum state and decoy
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "intangible_timer", 0.0) == 0.5

    # Assert a decoy was left behind
    assert len(world.balls) == 3
    decoy = world.balls[-1]
    assert getattr(decoy, "decoy_type", "") == "dash_decoy"
    assert decoy.x == 950.0
    assert decoy.y == 500.0
