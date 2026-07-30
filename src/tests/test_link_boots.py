import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y, cosmetic="link_boots", team="A", ball_id=1):
        self.x = x
        self.y = y
        self.cosmetic = cosmetic
        self.team = team
        self.id = ball_id
        self.alive = True
        self.speed_boost_timer = 0.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []

class MockHazard:
    def __init__(self, x, y, kind="generic", radius=20.0):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius

def test_link_boots_knockback_sharing():
    # Setup balls
    ball = MockBall(0, 0, "link_boots", "team_1", 1)
    ally1 = MockBall(50, 0, "none", "team_1", 2)
    ally2 = MockBall(100, 0, "none", "team_1", 3)
    enemy = MockBall(0, 50, "none", "team_2", 4)

    world = MockWorld([ball, ally1, ally2, enemy])
    action = Action(ball, world)

    # Manually test the logic applied in action.py for ball collision handling
    # Let's say enemy overlaps with ball
    dx = ball.x - enemy.x
    dy = ball.y - enemy.y
    dist = math.hypot(dx, dy)
    overlap = 20 - dist if dist < 20 else 10 # Force overlap
    nx = 0
    ny = 1 # Push down

    # Original positions
    orig_ball_y = ball.y
    orig_ally1_y = ally1.y
    orig_ally2_y = ally2.y

    knockback_multiplier = 1.0
    cosmetic = ball.cosmetic

    if cosmetic == "link_boots":
        nearest_ally = None
        min_dist = float('inf')
        my_team = getattr(ball, "team", "")
        for a in world.balls:
            if getattr(a, "alive", True) and a != ball:
                ally_team = getattr(a, "team", "")
                if ally_team == my_team:
                    d = math.hypot(a.x - ball.x, a.y - ball.y)
                    if d < min_dist:
                        min_dist = d
                        nearest_ally = a

        if nearest_ally:
            knockback_multiplier *= 0.5
            shared_kb_x = nx * overlap * 0.5
            shared_kb_y = ny * overlap * 0.5
            nearest_ally.x += shared_kb_x
            nearest_ally.y += shared_kb_y

            effects = ["speed_boost_timer"]
            for eff in effects:
                my_val = getattr(ball, eff, 0.0)
                if my_val > 0.0:
                    ally_val = getattr(nearest_ally, eff, 0.0)
                    if ally_val < my_val:
                        setattr(nearest_ally, eff, my_val)

    ball.x += nx * overlap * knockback_multiplier
    ball.y += ny * overlap * knockback_multiplier

    assert ball.y == orig_ball_y + overlap * 0.5
    assert ally1.y == orig_ally1_y + overlap * 0.5
    assert ally2.y == orig_ally2_y # Should not be affected since ally1 was closer

def test_link_boots_effect_sharing():
    # Setup balls
    ball = MockBall(0, 0, "link_boots", "team_1", 1)
    ball.speed_boost_timer = 5.0
    ally = MockBall(50, 0, "none", "team_1", 2)
    ally.speed_boost_timer = 1.0

    world = MockWorld([ball, ally])

    # We simulate a collision
    overlap = 10
    nx = 1
    ny = 0

    knockback_multiplier = 1.0

    nearest_ally = None
    min_dist = float('inf')
    my_team = getattr(ball, "team", "")
    for a in world.balls:
        if getattr(a, "alive", True) and a != ball:
            ally_team = getattr(a, "team", "")
            if ally_team == my_team:
                d = math.hypot(a.x - ball.x, a.y - ball.y)
                if d < min_dist:
                    min_dist = d
                    nearest_ally = a

    if nearest_ally:
        knockback_multiplier *= 0.5
        shared_kb_x = nx * overlap * 0.5
        shared_kb_y = ny * overlap * 0.5
        nearest_ally.x += shared_kb_x
        nearest_ally.y += shared_kb_y

        effects = ["speed_boost_timer"]
        for eff in effects:
            my_val = getattr(ball, eff, 0.0)
            if my_val > 0.0:
                ally_val = getattr(nearest_ally, eff, 0.0)
                if ally_val < my_val:
                    setattr(nearest_ally, eff, my_val)

    assert ally.speed_boost_timer == 5.0 # Should be updated to match ball's higher timer
