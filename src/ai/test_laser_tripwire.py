import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100.0
        self.radius = 10.0
        self.stun_timer = 0.0
        self.ball_type = "test"
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 100
        self.speed = 100
        self.friction_multiplier = 1.0
        self.pull_immune_timer = 0.0
        self.skill = "laser_tripwire"
        self.base_speed = 100

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 1
        self.events = []
        self.boosters = []

    def add_event(self, name, data):
        self.events.append((name, data))

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

def test_laser_tripwire_skill():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "A")
    b2 = MockBall(2, 50, 0, "B") # Enemy nearby
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._process_physics = lambda dt: None
    action._get_enemies = lambda: [b2]

    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "laser_tripwire"
    assert hazard.team == "A"
    assert b1.skill_timer == 10.0

    # Check physics logic when enemy touches tripwire
    b2_action = Action(b2, world)

    b2_action.execute("idle", 1.0)

    assert b2.hp in (-30.0, 0.0)
    assert b2.stun_timer == 2.0
    assert b2.id in hazard.hit_ids

    # Second tick, should not hit again
    world.tick = 2
    b2_action.execute("idle", 1.0)
    assert b2.hp in (-30.0, -130.0, 0.0)
