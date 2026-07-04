from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.profile_manager = MockProfileManager()
        self.balls = []
        self.arena = MockArena()

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

class MockProfileManager:
    def is_nemesis(self, t1, t2):
        if t1 == "basic" and t2 == "nemesis": return True
        return False

class MockBall:
    def __init__(self, id, ball_type, x, y):
        self.id = id
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = 100
        self.team = "Red"
        self.inventory = ["nemesis_compass_item"]

def test_nemesis_compass():
    world = MockWorld()
    ball = MockBall(1, "basic", 0, 0)
    enemy = MockBall(2, "nemesis", 100, 100)
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action.execute("attack", 1.0)

    assert "nemesis_compass_item" not in ball.inventory

    found_event = False
    for ev in world.events:
        if ev['type'] == 'nemesis_compass':
            found_event = True
            assert ev['data']['target_x'] == 100
            assert ev['data']['target_y'] == 100
    assert found_event
