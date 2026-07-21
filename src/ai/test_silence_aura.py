import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team, ball_type="silencer"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.skill = "silence_aura"
        self.skill_timer = 0.0
        self.silence_timer = 0.0
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100
        self.base_speed = 5.0
        self.speed = 5.0
        self.is_dashing = False
        self.used_skill = False
        self.active_skill = None
        self.charge_level = 0
        self.base_damage = 10

    def use_skill(self):
        self.used_skill = True
        return True

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.dead_balls = []

def test_silence_aura_applies_timer():
    attacker = MockBall(1, 0, 0, "team1")
    attacker.skill = "silence_aura"
    attacker.active_skill = "silence_aura"

    enemy_close = MockBall(2, 100, 0, "team2") # Dist 100 < 150
    enemy_far = MockBall(3, 200, 0, "team2")   # Dist 200 > 150
    ally = MockBall(4, 50, 0, "team1")         # Same team

    world = MockWorld([attacker, enemy_close, enemy_far, ally])

    action = Action(attacker, world)
    action._get_enemies = lambda: [enemy_close, enemy_far]

    action._use_skill()

    assert enemy_close.silence_timer == 3.0
    assert enemy_far.silence_timer == 0.0
    assert ally.silence_timer == 0.0

def test_silence_blocks_skills():
    ball = MockBall(1, 0, 0, "team1")
    ball.silence_timer = 3.0
    ball.skill = "dash"

    world = MockWorld([ball])

    action = Action(ball, world)
    action._use_skill()

    # use_skill should not be called because silence_timer > 0
    assert not ball.used_skill

def test_silence_timer_decrements():
    ball = MockBall(1, 0, 0, "team1")
    ball.silence_timer = 3.0

    world = MockWorld([ball])

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.silence_timer == 2.0

def test_silence_blocks_dash():
    ball = MockBall(1, 0, 0, "team1")
    ball.silence_timer = 3.0
    ball.stamina = 100

    world = MockWorld([ball])
    action = Action(ball, world)

    action.execute("chase", 1.0)

    assert not ball.is_dashing
    assert ball.speed == ball.base_speed
