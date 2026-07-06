import pytest
from ai.action import Action
from ai.perception import Perception
from ai.ball_types_tracker import Tracker

class MockHazard:
    def __init__(self, x, y, kind):
        self.id = id(self)
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 80.0
        self.last_updated_tick = 0

class MockEnemy:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.team = "enemy"
        self.has_stealth_drone = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.is_night = False
        self.is_lunar_eclipse = False
        self.is_foggy = False
        self.is_raining = False
        self.is_windy = False
        self.is_sandstorming = False
        self.is_snowing = False
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.tick = 0

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

    def get_nearby_entities(self, ball, radius):
        enemies = []
        for b in self.balls:
            if b.id != ball.id and b.team != ball.team:
                dist = ((b.x - ball.x)**2 + (b.y - ball.y)**2)**0.5
                if dist <= radius:
                    enemies.append(b)
        return {"enemies": enemies, "allies": [], "boosters": [], "traps": []}

def test_tracker_use_skill():
    ball = Tracker(1, 0.0, 0.0)
    ball.team = "allies"
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    # Try using the skill
    ball.skill_timer = 0.0
    action._use_skill()

    # The timer should be set for the sonar ping
    assert ball.sonar_ping_timer == 5.0
    assert ball.skill_timer == 12.0

    # Event should be emitted
    sonar_events = [e for e in world.events if e["type"] == "sonar_ping"]
    assert len(sonar_events) == 1
    assert sonar_events[0]["data"]["radius"] == 1500.0

def test_sonar_ping_perception_stealth():
    ball = Tracker(1, 0.0, 0.0)
    ball.team = "allies"
    world = MockWorld()
    world.balls.append(ball)

    # Add enemy far away (normally hidden due to stealth requiring distance < 80)
    enemy = MockEnemy(200.0, 0.0)
    world.balls.append(enemy)

    # With no sonar ping, enemy should be hidden by stealth
    perception = Perception(ball, world)
    data = perception.scan()
    assert len(data["enemies"]) == 0

    # Activate sonar ping
    ball.sonar_ping_timer = 5.0
    data = perception.scan()
    # With sonar ping active, enemy should be visible
    assert len(data["enemies"]) == 1
    assert data["enemies"][0].id == enemy.id

def test_sonar_ping_perception_smoke():
    ball = Tracker(1, 0.0, 0.0)
    ball.team = "allies"
    world = MockWorld()
    world.balls.append(ball)

    # Add enemy behind smoke
    enemy = MockEnemy(60.0, 0.0)
    enemy.has_stealth_drone = False
    world.balls.append(enemy)

    smoke = MockHazard(30.0, 0.0, "smokescreen"); smoke.radius = 20.0
    world.arena.hazards.append(smoke)

    # Without sonar ping, enemy is hidden behind smoke
    perception = Perception(ball, world)
    data = perception.scan()
    assert len(data["enemies"]) == 0

    # With sonar ping, enemy is visible despite smoke
    ball.sonar_ping_timer = 5.0
    data = perception.scan()
    assert len(data["enemies"]) == 1
    assert data["enemies"][0].id == enemy.id
