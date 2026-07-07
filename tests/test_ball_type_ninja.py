import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_ninja import Ninja

class MockTarget:
    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0, radius=10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius

def test_ninja_initialization():
    ball = Ninja(ball_id=1, x=10.0, y=20.0)

    assert ball.id == 1
    assert ball.x == 10.0
    assert ball.y == 20.0

    assert ball.BALL_TYPE == "ninja"
    assert ball.hp == 90.0
    assert ball.max_hp == 90.0
    assert ball.SPEED == 7.0
    assert ball.DAMAGE == 25
    assert ball.RADIUS == 8
    assert ball.PERCEPTION_RADIUS == 350
    assert ball.AGGRESSION == 0.8
    assert ball.COLOR == "black"
    assert ball.SKILL == "wall_jump"
    assert ball.SKILL_COOLDOWN == 4.0
    assert ball.ATTACK_RANGE == 21.0

    assert ball.alive is True
    assert ball.kills == 0
    assert ball.first_hit_taken is False
    assert ball.current_action == "idle"
    assert ball.skill_timer == 0.0
    assert ball.attack_timer == 0.0
    assert ball.attack_range == 21.0
    assert ball.personality.character == "cunning"

def test_ninja_hp_percent():
    ball = Ninja(ball_id=2)
    assert ball.get_hp_percent() == 1.0

    ball.take_damage(32.5)
    assert ball.get_hp_percent() == ball.hp / ball.max_hp
    assert ball.first_hit_taken is True

def test_ninja_take_damage_death():
    ball = Ninja(ball_id=3)
    ball.take_damage(90.0)
    assert ball.hp <= 0
    assert ball.alive is False

def test_ninja_actions():
    ball = Ninja(ball_id=4)

    ball.flee(0.1)
    assert ball.current_action == "flee"

    ball.attack(0.1)
    assert ball.current_action == "flank"

    ball.defend(0.1)
    assert ball.current_action == "defend"

    ball.collect_booster(0.1)
    assert ball.current_action == "opportunistic"

    ball.idle(0.1)
    assert ball.current_action == "idle"

def test_ninja_use_skill():
    ball = Ninja(ball_id=5)

    # Should use skill initially
    assert ball.use_skill() is True
    assert ball.skill_timer == ball.SKILL_COOLDOWN

    # Shouldn't use skill on cooldown
    assert ball.use_skill() is False

def test_ninja_repr():
    ball = Ninja(ball_id=6)
    repr_str = repr(ball)
    assert "ninja#6" in repr_str
    assert f"HP={ball.hp}/{ball.max_hp}" in repr_str
    assert "[idle]" in repr_str

def test_ninja_flank_movement():
    ball = Ninja(ball_id=7, x=0.0, y=0.0)
    target = MockTarget(x=100.0, y=0.0, vx=1.0, vy=0.0)

    # Flank point should be behind target: 100 - (10 * 2 + 20) = 100 - 40 = 60
    # The ball is at (0, 0), it should move to the right.
    old_x = ball.x

    ball.flank(1.0, target)

    assert ball.current_action == "flank"
    assert ball.x > old_x

def test_ninja_flank_skill_usage():
    ball = Ninja(ball_id=8, x=0.0, y=0.0)
    target = MockTarget(x=100.0, y=0.0, vx=1.0, vy=0.0)

    # direct_dist = 100
    # attack_range = 8 + 10 + 5 = 23
    # 23 * 1.5 = 34.5
    # direct_dist > 34.5, so skill should be used to close gap
    ball.skill_timer = 0.0

    ball.flank(0.01, target)

    assert ball.skill_timer == ball.SKILL_COOLDOWN

def test_ninja_flank_critical_hit():
    # The ball is behind the target and close enough to attack
    ball = Ninja(ball_id=9, x=78.0, y=0.0) # Within attack range (23) of target (100, 0)
    target = MockTarget(x=100.0, y=0.0, vx=1.0, vy=0.0)

    # Ball is at 78, target at 100. Vector is (22, 0).
    # Normal vector to target is (1, 0)
    # Target is moving at (1, 0)
    # Dot product: 1 * 1 + 0 * 0 = 1.0 > 0.5 (Critical)

    ball.attack_timer = 0.0

    # Should deal 3x damage
    ball.flank(0.0, target)

    assert ball.attack_timer > 0.0
    assert getattr(ball, "damage", 25.0) == ball.DAMAGE * 3.0

def test_ninja_flank_normal_hit():
    # The ball is in front of the target, so not a critical hit
    ball = Ninja(ball_id=10, x=122.0, y=0.0) # Within attack range (23) of target (100, 0)
    target = MockTarget(x=100.0, y=0.0, vx=1.0, vy=0.0)

    # Ball is at 122, target at 100. Vector is (-22, 0).
    # Normal vector to target is (-1, 0)
    # Target is moving at (1, 0)
    # Dot product: -1 * 1 + 0 * 0 = -1.0 <= 0.5 (Normal)

    ball.attack_timer = 0.0

    ball.flank(0.0, target)

    assert ball.attack_timer > 0.0
    assert getattr(ball, "damage", 25.0) == float(ball.DAMAGE)
