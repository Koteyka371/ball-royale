import pytest
from ai.action import Action
from ai.game_modes import DayNightMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": []}
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.skill = "deploy_sunlight_reflector"
        self.skill_timer = 0.0
        self.speed = 0.0
        self.speed_multiplier = 1.0

def test_deploy_sunlight_reflector():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls = [ball]
    action = Action(ball, world)

    # Trigger skill
    ball.skill = "deploy_sunlight_reflector"
    ball.skill_timer = 0.0
    action._use_skill()

    reflectors = [h for h in world.arena.hazards if getattr(h, "kind", "") == "sunlight_reflector"]
    assert len(reflectors) == 1
    ref = reflectors[0]
    assert getattr(ref, "duration", 0) == 20.0
    assert getattr(ref, "radius", 0) == 20.0
    assert getattr(ref, "team", "") == "A"

def test_day_night_sunlight_reflector():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls = [ball]

    mode = DayNightMode()
    mode.setup(world, world.balls)

    class SunlightReflectorNode:
        pass
    ref = SunlightReflectorNode()
    ref.kind = "sunlight_reflector"
    ref.x = 200
    ref.y = 200
    ref.radius = 20.0
    world.arena.hazards.append(ref)

    # Simulate a beam hitting the reflector
    beam = {'x': 200.0, 'y': 200.0, 'radius': 50.0, 'duration': 2.0}
    mode.active_sunlight_beams.append(beam)

    mode.tick(world, world.balls, delta=0.1)

    # Beam should be consumed, and 3 smaller beams created
    assert beam not in mode.active_sunlight_beams
    assert len(mode.active_sunlight_beams) == 3
    for b in mode.active_sunlight_beams:
        assert b['bounced'] == True
        assert b['radius'] == 25.0 # 50 * 0.5
