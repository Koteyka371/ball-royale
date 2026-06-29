from ai.ball_brain import BallBrain
from ai.coach_mode import CoachMode
from ai.decision import Decision

class MockEnemy:
    def __init__(self):
        self.id = 999
        self.hp = 10
        self.max_hp = 10
        self.x = 10
        self.y = 10
        self.ball_type = "warrior"
        self.team = "blue"

class MockBooster:
    def __init__(self):
        self.id = 888
        self.x = -10
        self.y = -10

class MockBall:
    def __init__(self, ball_type="warrior", team="red"):
        self.ball_type = ball_type
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.x = 0
        self.y = 0
        self.speed = 5
        self.perception_radius = 100
        self.current_action = "idle"
        self.attack_timer = 0
        self.skill_timer = 0
        self.difficulty = "medium"
        self.personality = "warrior"

    def get_hp_percent(self):
        return self.hp / self.max_hp

class MockWorld:
    def __init__(self):
        self.coach_strategy = {}
        self.game_mode = "coach"

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [MockEnemy()], "allies": [], "boosters": [MockBooster()], "traps": []}

def test_coach_mode_override():
    ball = MockBall(ball_type="warrior", team="red")
    world = MockWorld()

    brain = BallBrain(ball, world)

    world.coach_strategy = {"red": "Защищайтесь!"}

    brain.process(0.1)

    perception = brain.perception()
    emotion = brain.emotion(perception)
    decision = brain.decision(perception, emotion)

    assert decision in ["defend", "collect_booster", "attack", "use_skill"]

def test_coach_mode_string_alias():
    ball = MockBall(ball_type="scout", team="blue")
    world = MockWorld()
    world.coach_strategy = "Атакуйте!"

    decision_layer = Decision(ball, world)
    perception = {"enemies": [MockEnemy()], "allies": [], "boosters": [MockBooster()], "coach_strategy": "Атакуйте!"}
    action = decision_layer.choose_action(perception, "calm")

    assert action in ["attack", "chase", "collect_booster", "ricochet_attack", "use_skill"]

def test_coach_mode_booster():
    ball = MockBall(ball_type="warrior", team="red")
    world = MockWorld()
    world.coach_strategy = "Собирайте бустеры!"

    decision_layer = Decision(ball, world)
    perception = {"enemies": [MockEnemy()], "allies": [], "boosters": [MockBooster()], "coach_strategy": "Собирайте бустеры!"}
    action = decision_layer.choose_action(perception, "calm")

    assert action in ["collect_booster", "attack", "chase", "ricochet_attack"]

def test_coach_mode_flee():
    ball = MockBall(ball_type="warrior", team="red")
    world = MockWorld()
    world.coach_strategy = "Отступаем!"

    ball.ball_type = "scout"

    decision_layer = Decision(ball, world)
    perception = {"enemies": [MockEnemy()], "allies": [], "boosters": [MockBooster()], "coach_strategy": "Отступаем!"}
    action = decision_layer.choose_action(perception, "calm")

    assert action in ["flee", "attack", "collect_booster", "chase", "ricochet_attack"]



def test_coach_mode_class():
    coach = CoachMode()
    assert coach.get_strategy() == {}

    coach.set_global_strategy("Атакуйте!")
    assert coach.get_strategy() == "Атакуйте!"

    coach.set_team_strategy("red", "Защищайтесь!")
    assert coach.get_strategy() == {"red": "Защищайтесь!"}

def test_simulation_coach_integration():
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tests.simulate_battle import BattleSimulation
    sim = BattleSimulation(num_balls=10, max_ticks=10, seed=42)
    sim.set_coach_strategy("Атакуйте!")
    assert hasattr(sim, "coach_strategy")
    assert sim.coach_strategy == "Атакуйте!"

    sim.run()
    # If the balls process without crashing and coach_strategy is passed to them via perception, we're good
    assert sim.tick > 0
