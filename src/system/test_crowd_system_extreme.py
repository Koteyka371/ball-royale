import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()

    def add_event(self, event_type, data=None):
        self.events.append({'type': event_type, 'data': data})

class MockBall:
    def __init__(self, id, team, ball_type):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.x = 0
        self.y = 0
        self.hp = 100
        self.max_hp = 100

def test_extreme_event_black_hole():
    world = MockWorld()
    system = CrowdSystem(world)

    # Setup state
    system.active_vote = {"type": "extreme_event", "options": ["spawn_black_hole", "extreme_weather"]}
    system.votes = {"spawn_black_hole": 10, "extreme_weather": 5}
    system.vote_timer = 1

    balls = [MockBall(1, "team1", "player")]

    system.tick(balls, [], 1)

    assert system.active_vote is None

    # Check for spawn hazard event
    spawn_events = [e for e in world.events if e['type'] == 'spawn_hazard']
    assert len(spawn_events) > 0
    assert spawn_events[0]['data']['kind'] == 'massive_black_hole'

    cheer_events = [e for e in world.events if e['type'] == 'crowd_cheer']
    assert len(cheer_events) > 0
    assert "BLACK HOLE" in cheer_events[0]['data']['message']

def test_extreme_event_weather():
    world = MockWorld()
    system = CrowdSystem(world)

    # Setup state
    system.active_vote = {"type": "extreme_event", "options": ["spawn_black_hole", "extreme_weather"]}
    system.votes = {"spawn_black_hole": 5, "extreme_weather": 10}
    system.vote_timer = 1

    balls = [MockBall(1, "team1", "player")]

    system.tick(balls, [], 1)

    assert system.active_vote is None

    # Check for weather transition event
    weather_events = [e for e in world.events if e['type'] == 'weather_transition']
    assert len(weather_events) > 0
    assert weather_events[0]['data']['new_weather'] in ['thunderstorm', 'blizzard', 'acid_rain']

    cheer_events = [e for e in world.events if e['type'] == 'crowd_cheer']
    assert len(cheer_events) > 0
    assert "WEATHER" in cheer_events[0]['data']['message']
