import sys
sys.path.insert(0, 'src')
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0, speed=5.0, ball_type="swarm", personality="swarm"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.radius = 10.0
        self.ball_type = ball_type
        self.personality = personality
        self.attack_timer = 0.0

class MockWorld:
    def _deal_damage(self, attacker, target):
        pass

def test_group_attack_movement():
    swarm_ball = MockBall(x=0, y=0)
    target = MockBall(x=0, y=100, ball_type="basic")
    ally1 = MockBall(x=100, y=0, ball_type="swarm")
    ally2 = MockBall(x=100, y=0, ball_type="swarm")

    action = Action(swarm_ball, MockWorld())
    action._get_enemies = lambda: [target]
    action._get_allies = lambda: [ally1, ally2]

    # Without allies, nx=0, ny=1
    # With allies at (100, 0), cnx=1, cny=0
    # Blend: nx = 0*0.6 + 1*0.4 = 0.4
    #        ny = 1*0.6 + 0*0.4 = 0.6
    # Normalized: length = sqrt(0.16 + 0.36) = sqrt(0.52) ≈ 0.72
    # expected nx ≈ 0.4 / 0.72 > 0, expected ny ≈ 0.6 / 0.72 > 0
    action._group_attack(delta=1.0)

    # It should have moved both right (towards allies) and up (towards target)
    assert swarm_ball.x > 0
    assert swarm_ball.y > 0
