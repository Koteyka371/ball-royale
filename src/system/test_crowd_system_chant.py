import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team, alive=True, x=0, y=0, ball_type="basic"):
        self.id = id
        self.team = team
        self.alive = alive
        self.x = x
        self.y = y
        self.ball_type = ball_type

def test_adrenaline_buff():
    world = MockWorld()
    system = CrowdSystem(world)

    balls = [
        MockBall(1, "Red", True, x=10, y=10),
        MockBall(2, "Red", True, x=20, y=20),
        MockBall(3, "Blue", True, x=30, y=30)
    ]

    for t in range(1, 201):
        system.excitement_level = 100.0
        system._check_events(balls, [{'tick': t-1, 'killer_id': 1, 'victim_id': 3}], t)

    assert system.consecutive_chants == 1
    assert system.last_chant_team == "Red"
    tempo_events = [e for e in world.events if e[0] == "audio_event" and e[1].get("sound") == "bgm_tempo_up"]
    assert len(tempo_events) == 1
    tempo_events = [e for e in world.events if e[0] == "audio_event" and e[1].get("sound") == "bgm_tempo_up"]
    assert len(tempo_events) == 1
    tempo_events = [e for e in world.events if e[0] == "audio_event" and e[1].get("sound") == "bgm_tempo_up"]
    assert len(tempo_events) == 1

    for t in range(201, 401):
        system.excitement_level = 100.0
        system._check_events(balls, [{'tick': t-1, 'killer_id': 1, 'victim_id': 3}], t)

    assert system.consecutive_chants == 2
    assert system.last_chant_team == "Red"

    assert not any(e[0] == "spawn_booster" and e[1].get("value") == 50.0 for e in world.events)

    for t in range(401, 601):
        system.excitement_level = 100.0
        system._check_events(balls, [{'tick': t-1, 'killer_id': 1, 'victim_id': 3}], t)

    assert system.consecutive_chants == 3

    booster_events = [e for e in world.events if e[0] == "spawn_booster" and e[1].get("value") == 50.0]
    visual_events_streak = [e for e in world.events if e[0] == "visual_effect" and e[1].get("type") == "chant_streak"]
    assert len(visual_events_streak) == 1
    assert visual_events_streak[0][1].get("team") == "Red"
    visual_events_buff = [e for e in world.events if e[0] == "visual_effect" and e[1].get("type") == "adrenaline_buff"]
    assert len(visual_events_buff) == 2
    assert len(booster_events) == 2

def test_adrenaline_buff_interrupted():
    world = MockWorld()
    system = CrowdSystem(world)

    balls = [
        MockBall(1, "Red", True, x=10, y=10),
        MockBall(2, "Red", True, x=20, y=20),
        MockBall(3, "Blue", True, x=30, y=30)
    ]

    for t in range(1, 201):
        system.excitement_level = 100.0
        system._check_events(balls, [{'tick': t-1, 'killer_id': 1, 'victim_id': 3}], t)

    assert system.consecutive_chants == 1
    assert system.last_chant_team == "Red"

    balls[0].team = "Blue"
    balls[1].team = "Blue"

    for t in range(201, 401):
        system.excitement_level = 100.0
        system._check_events(balls, [{'tick': t-1, 'killer_id': 1, 'victim_id': 3}], t)

    assert system.consecutive_chants == 1
    assert system.last_chant_team == "Blue"
    reset_events = [e for e in world.events if e[0] == "audio_event" and e[1].get("sound") == "bgm_tempo_reset"]
    assert len(reset_events) == 1
