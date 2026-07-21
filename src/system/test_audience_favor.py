import pytest
from system.crowd_system import CrowdSystem

class MockBall:
    def __init__(self, id):
        self.id = id
        self.alive = True
        self.ball_type = "player"
        self.team = "Team1"
        self.hp = 100
        self.max_hp = 100
        self.audience_favor = 0.0
        self.attack_timer = 2.0
        self.skill_timer = 5.0
        self.x = 0.0
        self.y = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_audience_favor_comeback():
    world = MockWorld()
    cs = CrowdSystem(world)
    balls = [MockBall(1)]
    # Make total enemies 3x killer team
    for i in range(2, 6):
        b = MockBall(i)
        b.team = "Team2"
        balls.append(b)

    assert balls[0].audience_favor == 0.0
    kill_info = {"killer_id": 1, "victim_id": 2}
    cs._handle_kill(kill_info, 1, balls)
    assert balls[0].audience_favor == 30.0

def test_audience_favor_multikill():
    world = MockWorld()
    cs = CrowdSystem(world)
    balls = [MockBall(1), MockBall(2)]

    kill_info = {"killer_id": 1, "victim_id": 2}
    cs._handle_kill(kill_info, 1, balls)
    cs._handle_kill(kill_info, 2, balls)
    cs._handle_kill(kill_info, 3, balls) # 3rd kill = streak

    assert balls[0].audience_favor == 20.0

def test_audience_favor_high_favor():
    import random
    random.seed(42) # predictability
    world = MockWorld()
    cs = CrowdSystem(world)
    b = MockBall(1)
    b.audience_favor = 60.0
    b.hp = 50.0

    # We run enough ticks to almost certainly trigger the random chance
    # Also verify decay
    for i in range(200):
        if b.audience_favor < 50.0:
            b.audience_favor = 60.0 # reset to test healing
        cs._process_audience_favor([b], i)

    assert b.hp > 50.0
    assert b.attack_timer < 2.0
    assert b.skill_timer < 5.0

def test_audience_favor_low_favor():
    import random
    random.seed(42)
    world = MockWorld()
    cs = CrowdSystem(world)
    b = MockBall(1)
    b.audience_favor = -60.0

    for i in range(500):
        if b.audience_favor > -50.0:
            b.audience_favor = -60.0
        cs._process_audience_favor([b], i)

    hazards = [e for e in world.events if e[0] == "spawn_hazard"]
    assert len(hazards) > 0
