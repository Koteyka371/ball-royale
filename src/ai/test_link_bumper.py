import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 200
        self.y = 200
        self.radius = 20
        self.damage = 0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        nx = max(radius, min(1000 - radius, x))
        ny = max(radius, min(1000 - radius, y))
        return (nx, ny, x != nx or y != ny)

class MockEventList(list):
    def append(self, event):
        super().append(event)

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0

    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball], 'allies': []}

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.radius = 10
        self.team = team
        self.ball_type = "basic"
        self.speed_multiplier = 1.0
        self.stamina = 100
        self.max_stamina = 100

def test_link_bumper():
    bumper = MockHazard("link_bumper")
    arena = MockArena([bumper])
    triggerer = MockBall(1, 190, 190, 1)  # Distance = sqrt(200) = ~14.1, which is < (20 + 10 = 30)
    enemy = MockBall(2, 500, 500, 2)
    world = MockWorld(arena, [triggerer, enemy])
    action = Action(triggerer, world)

    action.execute("none", 0.1)

    # Check if bounced
    assert triggerer.vx != 0.0
    assert triggerer.vy != 0.0

    # Enemy velocity should be mirroring triggerer
    assert enemy.vx != 0.0
    assert enemy.vy != 0.0

    # Check speed boost timers
    assert getattr(triggerer, "speed_boost_timer", 0.0) > 0.0
    assert getattr(enemy, "speed_boost_timer", 0.0) == 2.0

    # Check visual event
    events = [e for e in world.events if e['type'] == 'visual_effect' and e['data']['type'] == 'link_line']
    assert len(events) == 1
