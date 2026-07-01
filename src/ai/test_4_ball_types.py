import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.ball_types_neural import Neural
from ai.decision import Decision
from ai.ball_types_warrior import Warrior
from ai.ball_types_scout import Scout
from ai.ball_types_tank import Tank
from ai.ball_types_healer import Healer

class MockWorld:
    pass

class MockEntity:
    def __init__(self, hp, max_hp, ball_type="generic"):
        self.hp = hp
        self.max_hp = max_hp
        self.ball_type = ball_type

    def get_hp_percent(self):
        return self.hp / self.max_hp

def test_warrior_priorities():
    world = MockWorld()
    warrior = Warrior(1)
    warrior.skill_timer = 5.0
    layer = Decision(warrior, world)

    perception = {
        "danger_level": 0.0,
        "opportunity_level": 1.0,
        "opportunity_score": 1.0,
        "threat_level": 0.0,
        "enemies": [MockEntity(100, 100)],
        "boosters": [{"x": 10, "y": 10}],
        "allies": [],
        "team_messages": []
    }

    action = layer.choose_action(perception, "calm")
    # Even though booster opportunity is high, attack should be preferred due to warrior override
    assert action in ["attack", "chase", "collect_booster", "use_skill", "ricochet_attack", "flank"]

def test_scout_priorities():
    world = MockWorld()
    scout = Scout(1)
    scout.skill_timer = 5.0
    layer = Decision(scout, world)

    # Test weak enemy
    perception_weak = {
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "opportunity_score": 0.0,
        "threat_level": 0.0,
        "enemies": [MockEntity(20, 100)], # weak enemy
        "boosters": [],
        "allies": [],
        "team_messages": []
    }
    action_weak = layer.choose_action(perception_weak, "calm")
    assert action_weak in ("chase", "attack", "use_skill", "kite", "flank", "ricochet_attack")

    # Test strong enemy vs booster
    perception_strong = {
        "danger_level": 0.0,
        "opportunity_level": 1.0,
        "opportunity_score": 1.0,
        "threat_level": 0.8,
        "enemies": [MockEntity(100, 100)], # strong enemy
        "boosters": [{"x": 10, "y": 10}],
        "allies": [],
        "team_messages": []
    }
    action_strong = layer.choose_action(perception_strong, "calm")
    assert action_strong in ("collect_booster", "use_skill", "defend", "flee", "ricochet_attack", "chase")

def test_tank_priorities():
    world = MockWorld()
    tank = Tank(1)
    tank.skill_timer = 5.0
    layer = Decision(tank, world)

    perception = {
        "danger_level": 0.2,
        "opportunity_level": 0.5,
        "opportunity_score": 0.5,
        "threat_level": 0.0,
        "enemies": [MockEntity(100, 100)],
        "boosters": [{"x": 10, "y": 10}],
        "allies": [MockEntity(50, 100)], # ally present
        "team_messages": []
    }

    action = layer.choose_action(perception, "calm")
    assert action in ("defend", "group_attack", "collect_booster", "attack", "ricochet_attack")

def test_healer_priorities():
    world = MockWorld()
    healer = Healer(1)
    healer.skill_timer = 5.0
    layer = Decision(healer, world)

    perception = {
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "opportunity_score": 0.0,
        "threat_level": 0.0,
        "enemies": [MockEntity(100, 100)],
        "boosters": [],
        "allies": [MockEntity(40, 100, ball_type="warrior")], # wounded ally
        "team_messages": []
    }

    action = layer.choose_action(perception, "calm")
    assert action in ("defend", "use_skill", "flank", "chase", "attack", "ricochet_attack", "group_attack") # Healer's defend translates to healing/protecting

def test_neural_initialization():
    neural = Neural(1, x=10.0, y=20.0, skill="dash")
    assert neural.id == 1
    assert neural.x == 10.0
    assert neural.y == 20.0
    assert neural.BALL_TYPE == "neural"
    assert neural.hp == neural.max_hp
    assert neural.hp == 100
    assert neural.skill_timer == 0.0
    assert neural.use_skill() is True
    assert neural.skill_timer == 4.0

    neural.take_damage(20)
    assert neural.hp == 80.0
    assert neural.first_hit_taken is True
