import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.speed = 2.0
        self.base_speed = 2.0
        self.attack_timer = 1.0
        self.skill_timer = 0.0
        self.base_skill_timer = 10.0
        self.skill = ""
        self.active_skill = ""
        self.time_warp_timer = 0.0
        self.time_warp_slow_timer = 0.0
        self.alive = True
        self.hp = 100
        self.inventory = []

class MockWorld:
    def __init__(self):
        self.balls = []

def test_time_warp_skill():
    world = MockWorld()
    attacker = MockBall(1, "team_a", 0, 0)
    attacker.skill = "time_warp"
    attacker.active_skill = "time_warp"

    nearby_enemy = MockBall(2, "team_b", 50, 0)  # within 150
    far_enemy = MockBall(3, "team_b", 200, 0)    # outside 150

    world.balls = [attacker, nearby_enemy, far_enemy]

    action = Action(attacker, world)

    # Trigger skill
    action._use_skill()
    assert attacker.time_warp_timer == 5.0

    # Execute one tick to apply buff/debuff
    action.execute("idle", 0.1)

    # Check attacker buff
    assert attacker.time_warp_timer == 4.9
    assert attacker.speed == 4.0
    # attacker.attack_timer was 1.0, decreased by delta * 1.5
    assert attacker.attack_timer < 1.0

    # Check nearby enemy debuff
    assert nearby_enemy.time_warp_slow_timer == 0.2

    # Check far enemy is unaffected
    assert far_enemy.time_warp_slow_timer == 0.0

    # Execute tick for nearby enemy to apply its slow
    action_enemy = Action(nearby_enemy, world)
    action_enemy.execute("idle", 0.1)
    assert abs(nearby_enemy.time_warp_slow_timer - 0.1) < 0.0001
    assert nearby_enemy.speed == nearby_enemy.base_speed * 0.4
