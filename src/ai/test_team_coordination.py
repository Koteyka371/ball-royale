import math
from src.ai.perception import Perception
from src.ai.decision import Decision
from src.ai.action import Action

class MockBall:
    def __init__(self, ball_id, x, y, hp=100, max_hp=100, ball_type="team_a", personality="idle"):
        self.id = ball_id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.ball_type = ball_type
        self.personality = personality
        self.speed = 2.0
        self.radius = 10.0
        self.perception_radius = 250.0
        self.alive = True
        self.skill_timer = 0.0
        self.current_action = "idle"
        self.team_message = None

    def get_hp_percent(self):
        return self.hp / self.max_hp

class MockWorld:
    def __init__(self, entities):
        self.entities = entities

    def get_nearby_entities(self, ball, radius):
        enemies = []
        allies = []
        for e in self.entities:
            if e.id != ball.id:
                dx = e.x - ball.x
                dy = e.y - ball.y
                if math.sqrt(dx*dx + dy*dy) <= radius:
                    if getattr(e, "ball_type", None) == ball.ball_type:
                        allies.append(e)
                    else:
                        enemies.append(e)
        return {
            "enemies": enemies,
            "allies": allies,
            "boosters": [],
            "traps": []
        }

def test_team_message_emission_help():
    ball = MockBall(1, 0, 0, hp=20, max_hp=100, personality="warrior")
    world = MockWorld([ball])
    action_layer = Action(ball, world)
    action_layer.execute("flee", 0.016)

    assert ball.team_message is not None
    assert ball.team_message["type"] == "help"

def test_team_message_emission_tank_hold():
    ball = MockBall(1, 0, 0, hp=100, max_hp=100, personality="tank")
    world = MockWorld([ball])
    action_layer = Action(ball, world)
    action_layer.execute("defend", 0.016)

    assert ball.team_message is not None
    assert ball.team_message["type"] == "hold"

def test_team_message_emission_target():
    ball = MockBall(1, 0, 0, personality="assassin")
    enemy = MockBall(2, 50, 0, ball_type="team_b")
    world = MockWorld([ball, enemy])
    action_layer = Action(ball, world)
    action_layer.execute("attack", 0.016)

    assert ball.team_message is not None
    assert ball.team_message["type"] == "target"
    assert ball.team_message["target_id"] == 2

def test_team_message_reception_defend():
    tank = MockBall(1, 50, 0, personality="tank")
    tank.team_message = {"type": "hold", "target_id": None}

    scout = MockBall(2, 0, 0, personality="scout")

    world = MockWorld([tank, scout])

    perc = Perception(scout, world)
    data = perc.scan()
    assert len(data["team_messages"]) == 1
    assert data["team_messages"][0]["type"] == "hold"

    dec = Decision(scout, world)
    # Give scout some danger to consider defend
    data["danger_level"] = 0.8
    action = dec.choose_action(data, "neutral")
    assert action == "defend"

def test_team_message_reception_attack():
    sniper = MockBall(1, 50, 0, personality="sniper")
    sniper.team_message = {"type": "threat", "target_id": 3}

    warrior = MockBall(2, 0, 0, personality="warrior")

    enemy = MockBall(3, 100, 0, ball_type="team_b")
    world = MockWorld([sniper, warrior, enemy])

    perc = Perception(warrior, world)
    data = perc.scan()

    assert len(data["team_messages"]) == 1

    dec = Decision(warrior, world)
    action = dec.choose_action(data, "neutral")

    assert action == "attack"
