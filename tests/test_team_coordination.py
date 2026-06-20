import sys
sys.path.insert(0, 'src')
from ai.decision import Decision

class MockBall:
    def __init__(self, b_type="warrior"):
        self.ball_type = b_type
        self.personality = b_type
        self.skill_timer = 0
        self.hp = 100
        self.max_hp = 100
        self.difficulty = "hard"

def test_team_coordination_decision():
    world = None

    perception_data = {
        "danger_level": 0.0,
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "opportunity_level": 0.0,
        "enemies": [1],
        "allies": [1],
        "boosters": [],
        "team_messages": []
    }

    # Test target_spotted for warrior
    ball = MockBall("warrior")
    decision = Decision(ball, world)
    action1 = decision.choose_action(perception_data, "calm")

    perception_data["team_messages"] = [{"type": "target_spotted", "x": 100, "y": 100}]
    action2 = decision.choose_action(perception_data, "calm")

    assert action1 in ["attack", "use_skill"] and action2 in ["attack", "use_skill"]

    # Test request_help for warrior
    perception_data["team_messages"] = [{"type": "request_help", "x": 100, "y": 100}]
    action3 = decision.choose_action(perception_data, "calm")
    assert action3 == "defend"

    # Test wounded_call for healer
    ball_healer = MockBall("healer")
    decision_healer = Decision(ball_healer, world)
    perception_data["team_messages"] = [{"type": "wounded_call", "x": 100, "y": 100}]
    action5 = decision_healer.choose_action(perception_data, "calm")
    assert action5 == "use_skill"

    # Test hold_position for tank
    ball_tank = MockBall("tank")
    decision_tank = Decision(ball_tank, world)
    perception_data["team_messages"] = [{"type": "hold_position", "x": 100, "y": 100}]
    action4 = decision_tank.choose_action(perception_data, "calm")
    assert action4 == "defend"
