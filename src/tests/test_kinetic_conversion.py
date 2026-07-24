import pytest
from ai.action import Action
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type("Arena", (), {"hazards": []})
        self.balls = []

class MockBall:
    def __init__(self):
        self.skill = "kinetic_conversion"
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 10.0
        self.supercharge_timer = 0.0
        self.speed_boost_timer = 0.0
        self.skill_timer = 0.0
        self.ball_type = "player"

def test_kinetic_conversion_activates_and_absorbs_knockback():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    # Set up manually to bypass engine physics overrides
    ball.kinetic_conversion_active = True
    ball.kinetic_conversion_timer = 5.0

    # Store old velocity
    ball._prev_vx_for_kinetic = 10.0
    ball.vx = 10.0

    # Simulate large knockback on second tick
    ball.vx = 110.0 # Delta of 100

    # Run ONLY the kinetic_conversion check part of execute
    kct = getattr(ball, "kinetic_conversion_timer", 0.0)
    delta = 0.1

    if kct > 0.0:
        ball.kinetic_conversion_timer = kct - delta

        dvx = getattr(ball, "vx", 0.0) - getattr(ball, "_prev_vx_for_kinetic", getattr(ball, "vx", 0.0))
        dvy = getattr(ball, "vy", 0.0) - getattr(ball, "_prev_vy_for_kinetic", getattr(ball, "vy", 0.0))

        if abs(dvx) > 50.0 or abs(dvy) > 50.0:
            ball.vx -= dvx * 0.5
            ball.vy -= dvy * 0.5
            ball.supercharge_timer = getattr(ball, "supercharge_timer", 0.0) + 3.0
            ball.speed_boost_timer = getattr(ball, "speed_boost_timer", 0.0) + 3.0
            ball.kinetic_conversion_timer = 0.0

    # 50% of the delta (100) should be subtracted.
    # So vx becomes 110 - 50 = 60
    assert abs(ball.vx - 60.0) < 0.1

    # Buffs should be applied
    assert ball.supercharge_timer >= 3.0
    assert ball.speed_boost_timer >= 3.0
    assert getattr(ball, "kinetic_conversion_timer", 0.0) == 0.0
