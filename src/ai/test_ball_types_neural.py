"""
Tests for: Neural ball type
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_neural import Neural

def test_neural_initialization():
    ball = Neural(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 100
    assert ball.max_hp == 100
    assert ball.alive is True
    assert ball.personality == "neural"

def test_neural_hp_percent():
    ball = Neural(ball_id=1)
    ball.hp = 50
    assert abs(ball.get_hp_percent() - 0.5) < 0.01

def test_neural_take_damage():
    ball = Neural(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 90
    assert ball.alive is True
    ball.take_damage(200)
    assert ball.alive is False

def test_neural_skill_and_predict():
    ball = Neural(ball_id=1)

    # Trigger use_skill
    assert ball.use_skill() is True
    assert ball.skill_timer == 5.0
    assert ball.use_skill() is False

    # Check that prediction was generated
    assert len(ball.last_prediction) == 2

    # Test specific neural predict values
    # inputs = [hp_percent=1.0, kills=0]
    # weights = [[0.1, -0.2], [-0.1, 0.3]]
    # biases = [0.5, -0.1]

    # Output 1: 0.5 + (1.0 * 0.1) + (0 * -0.2) = 0.5 + 0.1 = 0.6
    # Output 2: -0.1 + (1.0 * -0.1) + (0 * 0.3) = -0.1 - 0.1 = -0.2

    pred = ball.last_prediction
    assert abs(pred[0] - 0.6) < 0.001
    assert abs(pred[1] - (-0.2)) < 0.001

    # Ensure ball action changed since pred[0] > pred[1]
    assert ball.current_action == "attack"

def test_neural_actions():
    ball = Neural(ball_id=1)
    ball.flee(0.016)
    assert ball.current_action == "flee"
    ball.attack(0.016)
    assert ball.current_action == "attack"
    ball.defend(0.016)
    assert ball.current_action == "defend"
    ball.collect_booster(0.016)
    assert ball.current_action == "opportunistic"
    ball.idle(0.016)
    assert ball.current_action == "idle"
