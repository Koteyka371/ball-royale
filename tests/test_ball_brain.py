import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain


class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle"):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.current_action = None

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
    ball = MockBall()
    world = MockWorld()
    world.entities["enemies"] = [MockBall(), MockBall()]
    world.entities["boosters"] = [1] # mock booster

    brain = BallBrain(ball, world)

    # Check if scan is called
    scan_called = False
    original_scan = brain.perception_system.scan
    def mock_scan():
        nonlocal scan_called
        scan_called = True
        return original_scan()

    brain.perception_system.scan = mock_scan

    data = brain.perception()

    assert scan_called, "perception_system.scan() should be called"
    assert len(data["enemies"]) == 2
    assert len(data["allies"]) == 0
    assert len(data["boosters"]) == 1
    # with the new distance fallback calculation, a distance of -1 gives a different threat score.
    # Threat for e: 0.2
    # if dist > 0 (dist is -1 so no extra threat)
    # danger = 0.2 * 2 = 0.4. Which matches original!
    # Opp for b: 0.3
    # opportunity = 0.3. Which matches original!
    assert data["danger_level"] == 0.4
    assert data["opportunity_level"] == 0.3


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
    ball = MockBall(hp=100, max_hp=100, personality="warrior")
    world = MockWorld()
    brain = BallBrain(ball, world)

    # Neutral state, nothing around -> personality
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision == "warrior"

    # High danger -> defend
    world.entities["enemies"] = [MockBall() for _ in range(4)] # danger_level = 0.8
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
    world.entities["boosters"] = [1, 2] # opportunity_level = 0.6
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
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    world.entities["enemies"] = [MockBall()]
    brain = BallBrain(ball, world)

    brain.process(0.1)
    # 1 enemy, hp 100 -> rage emotion (hp>80%, enemies>0). decision attack
    assert ball.current_action == "attack"
