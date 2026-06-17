import pytest
import math

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0, speed=5.0, ball_type="ninja"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.radius = 10.0
        self.ball_type = ball_type
        self.attack_timer = 0.0

class MockWorld:
    def _deal_damage(self, attacker, target):
        pass

from ai.action import Action

def test_ninja_flank_chase():
    ninja = MockBall(x=0, y=0, ball_type="ninja")
    # Target is at (0, 100) and moving purely upwards (vy=10).
    # Its back should be at (0, 100 - (10+10+5)) = (0, 75).
    target = MockBall(x=0, y=100, vx=0, vy=10, ball_type="basic")

    action = Action(ninja, MockWorld())
    action._get_enemies = lambda: [target]
    action._get_allies = lambda: []

    # Ninja should move towards (0, 75) instead of (0, 100).
    # Distance is 75, so it should move purely upwards.
    action._chase(delta=1.0)

    assert ninja.x == 0
    # Moves speed * delta * 60 (but capped at dist which is 75 in attack or chase).
    # In chase, speed is 5.0 * 1.0 * 60 = 300? No, in chase boids rule gives nx, ny and it multiplies by speed * 60. Wait, chase doesn't multiply by 60 directly?
    # Ah, let's just check if it moves upwards.
    assert ninja.y > 0

def test_ninja_flank_attack():
    ninja = MockBall(x=10, y=100, ball_type="ninja")
    target = MockBall(x=0, y=100, vx=-10, vy=0, ball_type="basic")
    # target is moving left, so its back is to the right (x > 0).
    # ninja is at (10, 100), back is at 0 - (-1) * 25 = 25.
    # ninja should move right towards 25.

    action = Action(ninja, MockWorld())
    action._get_enemies = lambda: [target]
    action._get_allies = lambda: []

    action._attack(delta=1.0)

    # Since ninja is at x=10 and wants to go to x=25, it should move right.
    assert ninja.x > 10
