import pytest
from src.ai.perception import Perception
from src.ai.decision import Decision
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.width = 800
        self.height = 600

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [ball], "boosters": [], "traps": []}

class MockBall:
    def __init__(self, ball_type, x, y, hp=100, max_hp=100):
        self.id = id(self)
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.radius = 10
        self.speed = 2.0
        self.skill_timer = 0.0
        self.perception_radius = 300
        self.current_action = "idle"
        self.team_message = ""
        self.personality = ball_type
        self.difficulty = "hard"

def test_tank_emits_hold_position():
    world = MockWorld()
    tank = MockBall("tank", 100, 100)
    action_layer = Action(tank, world)

    action_layer.execute("defend", 0.016)

    assert tank.team_message == "hold_position"

def test_healer_emits_call_for_wounded():
    world = MockWorld()
    healer = MockBall("healer", 100, 100)
    action_layer = Action(healer, world)

    action_layer.execute("idle", 0.016)

    assert healer.team_message == "call_for_wounded"

def test_sniper_emits_threat():
    world = MockWorld()
    sniper = MockBall("sniper", 100, 100)
    action_layer = Action(sniper, world)

    action_layer.execute("attack", 0.016)

    assert sniper.team_message == "threat"

def test_flee_emits_request_help():
    world = MockWorld()
    ball = MockBall("warrior", 100, 100)
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.016)

    assert ball.team_message == "request_help"

def test_decision_influenced_by_hold_position():
    world = MockWorld()
    ball = MockBall("warrior", 100, 100)
    decision_layer = Decision(ball, world)

    perception_data_normal = {
        "enemies": [], "allies": [], "boosters": [], "traps": [],
        "team_messages": [], "danger_level": 0.0, "threat_level": 0.0,
        "opportunity_level": 0.0, "opportunity_score": 0.0
    }
    action_normal = decision_layer.choose_action(perception_data_normal, "calm")

    perception_data_with_signal = {
        "enemies": [], "allies": [], "boosters": [], "traps": [],
        "team_messages": ["hold_position"], "danger_level": 0.0, "threat_level": 0.0,
        "opportunity_level": 0.0, "opportunity_score": 0.0
    }
    action_with_signal = decision_layer.choose_action(perception_data_with_signal, "calm")

    # Normally a warrior defaults to its personality or idle if nothing is happening
    # With "hold_position", defend should score much higher
    assert action_with_signal == "defend"

def test_decision_influenced_by_call_for_wounded_when_low_hp():
    world = MockWorld()
    ball = MockBall("warrior", 100, 100, hp=20, max_hp=100)  # Low HP
    decision_layer = Decision(ball, world)

    perception_data = {
        "enemies": [], "allies": [], "boosters": [], "traps": [],
        "team_messages": ["call_for_wounded"], "danger_level": 0.0, "threat_level": 0.0,
        "opportunity_level": 0.0, "opportunity_score": 0.0
    }

    # Warrior default might be attack or idle, but low hp + call_for_wounded should boost flee significantly
    action = decision_layer.choose_action(perception_data, "calm")
    assert action == "flee"
