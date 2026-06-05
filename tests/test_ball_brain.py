import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain


class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle", x=0, y=0, perception_radius=300):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.current_action = None
        self.x = x
        self.y = y
        self.perception_radius = perception_radius
        self.id = "mock_ball"

    def flee(self, delta):
        pass

    def attack(self, delta):
        pass

    def defend(self, delta):
        pass

    def collect_booster(self, delta):
        pass

    def idle(self, delta):
        pass


class MockWorld:
    def __init__(self):
        self.entities = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": []
        }

    def get_nearby_entities(self, ball, radius):
        return self.entities


def test_ball_brain_initialization():
    ball = MockBall()
    world = MockWorld()
    brain = BallBrain(ball, world)

    assert brain.ball == ball
    assert brain.world == world


def test_perception_layer():
    ball = MockBall(x=0, y=0, perception_radius=100)
    world = MockWorld()

    # 2 enemies right on top of ball (dist 0), so each gives 0.5 danger
    world.entities["enemies"] = [MockBall(x=0, y=0), MockBall(x=0, y=0)]
    # 1 booster right on top (dist 0), gives 0.6 opportunity
    class MockBooster:
        x = 0
        y = 0
        id = "mock_booster"
    world.entities["boosters"] = [MockBooster()]

    brain = BallBrain(ball, world)
    data = brain.perception()

    assert len(data["enemies"]) == 2
    assert len(data["allies"]) == 0
    assert len(data["boosters"]) == 1
    # danger = 2 * 0.5 = 1.0
    assert data["danger_level"] == 1.0
    # opp = 1 * 0.6 = 0.6
    assert data["opportunity_level"] == 0.6


def test_emotion_layer():
    ball = MockBall(hp=20, max_hp=100) # 20% HP
    world = MockWorld()
    brain = BallBrain(ball, world)

    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    assert emotion == "fear"

    ball.hp = 100
    world.entities["boosters"] = [1]
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    assert emotion == "greed"

    ball.hp = 100
    world.entities["boosters"] = []
    world.entities["enemies"] = [MockBall()]
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    assert emotion == "rage"


def test_decision_layer():
    ball = MockBall(hp=100, max_hp=100, personality="warrior", x=0, y=0, perception_radius=100)
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Neutral state, nothing around -> personality
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision == "warrior"

    # High danger -> defend
    for _ in range(4):
        b = MockBall(x=0, y=0)
        b.id = str(len(world.entities["enemies"]))
        world.entities["enemies"].append(b)

    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision == "defend"

    # Low HP -> flee
    ball.hp = 20
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision == "flee"

    # Greed / Booster -> opportunistic
    ball.hp = 100
    world.entities["enemies"] = []

    class MockBooster:
        def __init__(self, id):
            self.id = id
            self.x = 0
            self.y = 0

    world.entities["boosters"] = [MockBooster(1), MockBooster(2)]
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision == "opportunistic"


def test_action_layer():
    ball = MockBall()
    world = MockWorld()
    brain = BallBrain(ball, world)

    brain.action("flee", 0.1)
    assert ball.current_action == "flee"

    brain.action("attack", 0.1)
    assert ball.current_action == "attack"


def test_full_process():
    ball = MockBall(hp=100, max_hp=100, x=0, y=0)
    world = MockWorld()
    world.entities["enemies"] = [MockBall(x=0, y=0)]
    brain = BallBrain(ball, world)

    brain.process(0.1)
    # 1 enemy, hp 100 -> rage emotion (hp>80%, enemies>0). decision attack
    assert ball.current_action == "attack"
