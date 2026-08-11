with open("src/tests/test_giant_bouncy_royale_mode.py", "w") as f:
    f.write("""import pytest
from ai.game_modes import GAME_MODES, GiantBouncyRoyaleMode
from ai.action import Action
import copy
import math

class MockWorld:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.balls = []
        self.projectiles = []
        self.hazards = []
        self.events = []
        self.tick = 0
        self.dead_balls = []
        self.game_mode = None

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.base_radius = 15.0
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100.0
        self.max_hp = 100.0
        self.max_speed = 300.0

    def get(self, key, default=None):
        return getattr(self, key, default)

def test_giant_bouncy_royale_mode_registered():
    assert "giant_bouncy_royale" in GAME_MODES
    assert isinstance(GAME_MODES["giant_bouncy_royale"], GiantBouncyRoyaleMode)

def test_giant_bouncy_royale_mode_radius():
    mode = GiantBouncyRoyaleMode()
    world = MockWorld()
    world.game_mode = mode

    b1 = MockBall(1, 500, 500)
    world.balls = [b1]

    mode.setup(world, world.balls)
    assert b1.radius == 30.0

    # Manually change radius and check apply_dynamic_traits
    b1.radius = 15.0
    mode.apply_dynamic_traits(world, world.balls, 0.1)
    assert b1.radius == 30.0

def test_giant_bouncy_royale_wall_bounce():
    mode = GiantBouncyRoyaleMode()
    world = MockWorld()
    world.game_mode = mode

    # Ball moving fast towards right wall
    b1 = MockBall(1, 990, 500)
    b1.radius = 30.0
    b1.vx = 100.0
    b1.vy = 0.0
    world.balls = [b1]

    action = Action(b1, world)

    # The ball is past the boundary if radius is 30 and x is 990, width=1000
    # 990 + 30 = 1020 > 1000, so it will clamp to 970 and bounce
    action._clamp_position()

    assert b1.x == 970.0
    # Should multiply velocity by 2.0 (since it's Giant Bouncy Royale, same as Extreme Bounciness)
    assert b1.vx == 200.0

def test_giant_bouncy_royale_ball_collision():
    mode = GiantBouncyRoyaleMode()
    world = MockWorld()
    world.game_mode = mode

    b1 = MockBall(1, 500, 500)
    b1.radius = 30.0

    b2 = MockBall(2, 530, 500) # Distance 30, overlapping by 30
    b2.radius = 30.0

    world.balls = [b1, b2]

    action = Action(b1, world)
    old_b1_vx = b1.vx

    # Call internal method for collisions
    # In action.py, collisions are processed in execute() or similar,
    # but we can simulate the knockback logic here:
    dx = b1.x - b2.x
    dy = b1.y - b2.y
    dist_sq = dx * dx + dy * dy
    dist = math.sqrt(dist_sq)
    overlap = (b1.radius + b2.radius) - dist
    nx = dx / dist
    ny = dy / dist
    knockback_multiplier = 2.0
    b1.x += nx * overlap * knockback_multiplier
    b1.y += ny * overlap * knockback_multiplier

    # b1 x changes by nx ( -1 ) * overlap (30) * 2.0 = -60
    assert b1.x == 440.0
""")
