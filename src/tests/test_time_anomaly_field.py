import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.tick = 0
        self.projectiles = []
        self.boosters = []
        self.next_id = 100
    def add_event(self, e, data=None):
        pass
    def get_nearby_entities(self, b, r):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": []}

class MockBall:
    def __init__(self, x=0, y=0, id=1, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.hp = 100.0
        self.stamina = 100.0
        self.skill = "deploy_time_anomaly_field"
        self.skill_timer = 0.0
        self.state_history = []
        self.base_speed = 0.0
        self.base_damage = 10.0
        self._base_speed_set = True
        self.vx = 0
        self.vy = 0

def test_deploy_time_anomaly_field():
    world = MockWorld()
    ball = MockBall(50, 50)
    world.balls = [ball]
    action = Action(ball, world)
    action._use_skill()
    fields = [h for h in world.arena.hazards if getattr(h, "kind", "") == "time_anomaly_field"]
    assert len(fields) == 1
    field = fields[0]
    assert field.x == 50
    assert field.y == 50
    assert field.radius == 150.0

def test_time_anomaly_field_effect():
    world = MockWorld()
    ball = MockBall(50, 50)
    past_state = {
        "x": 10.0,
        "y": 10.0,
        "hp": 50.0,
        "stamina": 30.0,
        "attack_timer": 0.0,
        "skill_timer": 0.0
    }
    ball.state_history.append(past_state)
    class FieldNode:
        pass
    field = FieldNode()
    field.kind = "time_anomaly_field"
    field.x = 50.0
    field.y = 50.0
    field.radius = 150.0
    world.arena.hazards.append(field)
    action = Action(ball, world)
    action.execute("idle", 1.0)
    assert abs(ball.x - 10.0) < 0.1
    assert abs(ball.y - 10.0) < 0.1
    assert ball.hp == 50.0
