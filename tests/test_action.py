import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockBall:
    def __init__(self):
        self.current_action = None
        self.calls = []

    def flee(self, delta):
        self.calls.append(("flee", delta))

    def attack(self, delta):
        self.calls.append(("attack", delta))

    def defend(self, delta):
        self.calls.append(("defend", delta))

    def collect_booster(self, delta):
        self.calls.append(("collect_booster", delta))

    def use_skill(self):
        self.calls.append(("use_skill",))

    def chase(self, delta):
        self.calls.append(("chase", delta))

    def idle(self, delta):
        self.calls.append(("idle", delta))

class MockWorld:
    pass

def test_action_initialization():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    assert action_layer.ball == ball
    assert action_layer.world == world

def test_execute_flee():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)
    assert ball.current_action == "flee"
    assert ("flee", 0.1) in ball.calls

def test_execute_attack():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)
    assert ball.current_action == "attack"
    assert ("attack", 0.1) in ball.calls

def test_execute_defend():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("defend", 0.1)
    assert ball.current_action == "defend"
    assert ("defend", 0.1) in ball.calls

def test_execute_collect_booster():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("collect booster", 0.1)
    assert ball.current_action == "collect booster"
    assert ("collect_booster", 0.1) in ball.calls

    # Also test the old terminology to ensure backward compatibility
    ball.calls.clear()
    action_layer.execute("opportunistic", 0.2)
    assert ball.current_action == "opportunistic"
    assert ("collect_booster", 0.2) in ball.calls

def test_execute_use_skill():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("use skill", 0.1)
    assert ball.current_action == "use skill"
    assert ("use_skill",) in ball.calls

def test_execute_chase():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("chase", 0.1)
    assert ball.current_action == "chase"
    assert ("chase", 0.1) in ball.calls

def test_execute_idle_fallback():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    # Unknown strategy should fallback to idle
    action_layer.execute("unknown_strategy", 0.1)
    assert ball.current_action == "unknown_strategy"
    assert ("idle", 0.1) in ball.calls
