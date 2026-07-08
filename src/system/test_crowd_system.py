import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, t, data):
        self.events.append((t, data))

class MockBall:
    def __init__(self, id, team, ball_type, alive=True):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.alive = alive
        self.x = 0.0
        self.y = 0.0

def test_check_camping():
    world = MockWorld()
    system = CrowdSystem(world)

    ball = MockBall(1, "red", "tank")
    balls = [ball]

    # Tick 51 times without moving
    for i in range(51):
        system.tick(balls, [], i)

    events = [e[0] for e in world.events]
    assert "crowd_throw" in events
    assert "spawn_hazard" in events

    hazard_events = [e for e in world.events if e[0] == "spawn_hazard" and e[1]["kind"] == "spike_trap"]
    assert len(hazard_events) > 0

def test_multikill_booster():
    world = MockWorld()
    system = CrowdSystem(world)

    ball = MockBall(1, "red", "tank")
    balls = [ball]

    kill_log = []

    for i in range(3):
        kill_log.append({
            "tick": i + 1,
            "killer_id": 1,
            "victim_id": i + 10
        })
        system.tick(balls, kill_log, i + 1)

    events = [e[0] for e in world.events]
    assert "spawn_booster" in events

    booster_events = [e for e in world.events if e[0] == "spawn_booster"]
    assert len(booster_events) > 0
    assert booster_events[-1][1]["kind"] == "speed"


def test_external_command_spawn():
    world = MockWorld()
    system = CrowdSystem(world)
    ball = MockBall(1, "red", "tank")
    ball.x = 100.0
    ball.y = 100.0
    balls = [ball]

    system.queue_external_command("TwitchUser1", "!spawn lava_pit 1")
    system.tick(balls, [], 1)

    events = [e[0] for e in world.events]
    assert "spawn_hazard" in events
    hazard_events = [e for e in world.events if e[0] == "spawn_hazard"]
    assert len(hazard_events) > 0
    assert hazard_events[-1][1]["kind"] == "lava_pit"
    assert hazard_events[-1][1]["x"] == 100.0

def test_external_command_drop():
    world = MockWorld()
    system = CrowdSystem(world)
    ball = MockBall(2, "blue", "speedster")
    ball.x = 200.0
    ball.y = 200.0
    balls = [ball]

    system.queue_external_command("TwitchUser2", "!drop shield 2")
    system.tick(balls, [], 1)

    events = [e[0] for e in world.events]
    assert "spawn_booster" in events
    booster_events = [e for e in world.events if e[0] == "spawn_booster"]
    assert len(booster_events) > 0
    assert booster_events[-1][1]["kind"] == "shield"
    assert booster_events[-1][1]["x"] == 200.0

def test_external_command_vote():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    import random
    old_random = random.random
    random.random = lambda: 1.0
    system.queue_external_command("TwitchUser3", "!vote lava")
    system.tick(balls, [], 1)
    random.random = old_random

    assert system.votes["lava"] == 1
    assert system.votes["spike"] == 0

def test_real_spectators_disable_simulated_votes():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    import random
    old_random = random.random
    random.random = lambda: 0.01  # Guarantee simulated vote if enabled

    # Tick without real spectators
    system.tick(balls, [], 1)
    # The simulated spectator should have cast a vote (since 0.01 < 0.05)
    total_votes = sum(system.votes.values())
    assert total_votes > 0

    # Clear votes and simulate real spectator joining
    system.votes = {"lava": 0, "spike": 0}
    system.queue_external_command("TwitchUser", "!vote spike")

    # Tick with real spectators
    system.tick(balls, [], 2)
    # The real user voted for spike
    # The simulated spectator should NOT have cast a vote
    assert system.votes["spike"] == 1
    assert system.votes["lava"] == 0
    total_votes_after = sum(system.votes.values())
    assert total_votes_after == 1

    random.random = old_random
