import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team, hp, max_hp, alive=True, ball_type="normal"):
        self.id = id
        self.team = team
        self.hp = hp
        self.max_hp = max_hp
        self.alive = alive
        self.ball_type = ball_type
        self.x = 0
        self.y = 0

def test_crowd_epic_kill():
    world = MockWorld()
    crowd = CrowdSystem(world)

    balls = [MockBall(1, "A", 100, 100)]
    kill_log = [
        {"tick": 10, "killer_id": 1, "victim_id": 2},
        {"tick": 20, "killer_id": 1, "victim_id": 3},
        {"tick": 30, "killer_id": 1, "victim_id": 4},
    ]

    crowd.tick(balls, kill_log[:1], 10)
    crowd.tick(balls, kill_log[:2], 20)
    crowd.tick(balls, kill_log[:3], 30)

    # Check if epic kill event was fired
    assert any(e[0] == "crowd_cheer" and "3-kill streak" in e[1]["message"] for e in world.events)
    assert any(e[0] == "audio_event" and e[1]["sound"] == "epic_crowd_roar" for e in world.events)
    assert crowd.excitement_level > 10.0

def test_crowd_comeback():
    world = MockWorld()
    crowd = CrowdSystem(world)

    # 1 ball on team A, 3 balls on team B
    balls = [
        MockBall(1, "A", 100, 100),
        MockBall(2, "B", 100, 100),
        MockBall(3, "B", 100, 100),
        MockBall(4, "B", 100, 100),
    ]
    kill_log = [{"tick": 10, "killer_id": 1, "victim_id": 2}]

    crowd.tick(balls, kill_log, 10)

    # Check if comeback event was fired
    assert any(e[0] == "crowd_cheer" and "comeback attempt" in e[1]["message"] for e in world.events)
    assert any(e[0] == "audio_event" and e[1]["sound"] == "comeback_cheer" for e in world.events)

def test_crowd_throw_buff():
    world = MockWorld()
    crowd = CrowdSystem(world)

    import random
    random.seed(42) # Try to get a hit for 1% chance

    crowd.excitement_level = 100.0
    balls = [
        MockBall(1, "A", 10, 100), # Low hp ball
        MockBall(2, "A", 100, 100)
    ]

    for i in range(1000):
        crowd.tick(balls, [], i)
        if any(e[0] == "spawn_booster" for e in world.events):
            break

    assert any(e[0] == "spawn_booster" for e in world.events)
    assert any(e[0] == "crowd_throw" for e in world.events)

def test_crowd_team_wipe():
    world = MockWorld()
    crowd = CrowdSystem(world)

    # 2 balls on team B, one dies earlier
    balls = [
        MockBall(1, "A", 100, 100),
        MockBall(2, "B", 0, 100, alive=False),
        MockBall(3, "B", 0, 100, alive=False), # The victim
    ]
    kill_log = [{"tick": 10, "killer_id": 1, "victim_id": 3}]

    crowd.tick(balls, kill_log, 10)

    # Check if team wipe event was fired
    assert any(e[0] == "crowd_cheer" and "is wiped out!" in e[1]["message"] for e in world.events)
    assert any(e[0] == "audio_event" and e[1]["sound"] == "team_wipe_gasp" for e in world.events)

def test_crowd_throw_hazard():
    world = MockWorld()
    crowd = CrowdSystem(world)

    import random
    random.seed(42)

    # Set excitement very low to simulate boring match
    crowd.excitement_level = 10.0

    balls = [
        MockBall(1, "A", 100, 100),
        MockBall(2, "B", 100, 100)
    ]

    for i in range(1000):
        crowd.tick(balls, [], i)
        if any(e[0] == "spawn_hazard" for e in world.events):
            break

    assert any(e[0] == "spawn_hazard" for e in world.events)
    assert any(e[0] == "crowd_throw" and "boos" in e[1]["message"] for e in world.events)
    assert crowd.excitement_level > 10.0
