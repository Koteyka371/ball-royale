import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain


class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle", skin="default"):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.skin = skin
        self.current_action = None
        self.x = 0
        self.y = 0
        self.speed = 10
        self.radius = 10
        self.perception_radius = 100
        self.ball_type = "mock"
        self.alive = True

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
    data = brain.perception()

    assert len(data["enemies"]) == 2
    assert len(data["allies"]) == 0
    assert len(data["boosters"]) == 1
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

    # Neutral state, nothing around -> personality behavior (attack for warrior)
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision in ["attack", "defend", "kite", "ricochet_attack", "target_weak", "intercept"]

    # High danger -> defend
    world.entities["enemies"] = [MockBall() for _ in range(4)] # danger_level = 0.8
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision in ["defend", "attack", "chase", "kite", "use_skill"]

    # Low HP -> flee
    ball.hp = 20
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision in ["flee", "defend", "attack", "use_skill", "flank", "kite", "chase"]

    # Greed / Booster -> opportunistic
    ball.hp = 100
    world.entities["enemies"] = []
    world.entities["boosters"] = [1, 2] # opportunity_level = 0.6
    perception_data = brain.perception()
    emotion = brain.emotion(perception_data)
    decision = brain.decision(perception_data, emotion)
    assert decision in ["collect_booster", "defend", "attack", "kite", "flank", "ricochet_attack", "escort", "target_weak", "use_skill", "flee", "chase", "idle", "group_attack", "hide_behind", "hold_zone", "intercept"]


def test_action_layer():
    ball = MockBall()
    world = MockWorld()
    brain = BallBrain(ball, world)

    brain.action("flee", 0.1)
    assert ball.current_action == "flee"

    brain.action("attack", 0.1)
    assert ball.current_action in ["attack", "chase", "use_skill"]


def test_full_process():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    world.entities["enemies"] = [MockBall()]
    brain = BallBrain(ball, world)

    brain.process(0.1)
    # 1 enemy, hp 100 -> rage emotion (hp>80%, enemies>0). decision attack
    assert ball.current_action in ["attack", "chase", "kite", "use_skill", "deploy_decoy_beacon", "flank", "hold_zone", "intercept"]


def test_skin_perks():
    ball = MockBall(hp=100, max_hp=100, skin="veteran")
    world = MockWorld()
    brain = BallBrain(ball, world)
    assert getattr(ball, "status_resistance", 0.0) == 0.02

    ball = MockBall(hp=100, max_hp=100, skin="legendary")
    brain = BallBrain(ball, world)
    assert getattr(ball, "has_aura", False) == True

    ball = MockBall(hp=100, max_hp=100, skin="elite")
    brain = BallBrain(ball, world)
    assert getattr(ball, "speed", 100.0) == 10.5


def test_prestige_upgrades():
    class MockProfileManager:
        def __init__(self, filename):
            self.data = {
                "bonuses": {},
                "prestige_level": 1,
                "prestige_tokens": 0,
                "prestige_upgrades": {
                    "permanent_hp": 2,
                    "permanent_speed": 1,
                    "permanent_damage": 3
                }
            }

    import sys
    sys.modules['system.profile'] = type('ProfileModule', (object,), {'ProfileManager': MockProfileManager})

    ball = MockBall(1, "warrior")
    ball.hp = 100
    ball.max_hp = 100
    ball.speed = 10
    ball.damage = 10

    from ai.ball_brain import BallBrain
    brain = BallBrain(ball, MockWorld())

    # max_hp += 2 * 10 = 20 -> 120
    # prestige_level stat multiplier = 1.05
    # max_hp *= 1.05 -> 126
    assert ball.max_hp == 126.0

    # speed += 1 * 5 = 15
    # speed *= 1.05 -> 15.75
    assert ball.speed == 15.75

    # damage += 3 * 2 = 16
    # damage *= 1.05 -> 16.8
    assert ball.damage == 16.8

    del sys.modules['system.profile']
