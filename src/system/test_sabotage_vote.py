import pytest
from system.crowd_system import CrowdSystem

class MockBall:
    def __init__(self, hp=100.0, speed=100.0, alive=True, ball_type="player"):
        self.hp = hp
        self.speed = speed
        self.base_speed = speed
        self.alive = alive
        self.ball_type = ball_type
        self.silence_timer = 0.0

class MockWorld:
    def add_event(self, event_type, data):
        pass

def test_player_sabotage_vote():
    world = MockWorld()
    system = CrowdSystem(world)

    b1 = MockBall(hp=100.0, speed=200.0)
    balls = [b1]

    # Force the start of a sabotage vote
    system.active_vote = {"type": "player_sabotage", "options": ["sluggish", "fragile", "silenced"]}
    system.votes = {"sluggish": 1, "fragile": 0, "silenced": 0}

    # Resolve the vote
    system._resolve_vote(balls)

    # Check that sabotage was applied
    assert getattr(b1, "crowd_sabotage_timer", 0) > 0
    assert getattr(b1, "crowd_sabotage_type", "") == "sluggish"

    # Process sabotage (tick)
    timer_initial = b1.crowd_sabotage_timer
    system._process_sabotage(balls, 0)

    assert b1.crowd_sabotage_timer == timer_initial - 1
    assert b1.speed == b1.base_speed * 0.5

    # Test fragile
    b2 = MockBall(hp=100.0)
    b2.crowd_sabotage_timer = 10
    b2.crowd_sabotage_type = "fragile"
    balls2 = [b2]

    system._process_sabotage(balls2, 0)
    assert b2.hp == 99.8

    # Test silenced
    b3 = MockBall()
    b3.crowd_sabotage_timer = 10
    b3.crowd_sabotage_type = "silenced"
    balls3 = [b3]

    system._process_sabotage(balls3, 0)
    assert b3.silence_timer == 2.0

    # Test expiration (timer hits 0)
    b4 = MockBall(speed=200.0)
    b4.crowd_sabotage_timer = 1
    b4.crowd_sabotage_type = "sluggish"
    b4.crowd_sabotage_speed_active = True
    b4.speed = 100.0
    balls4 = [b4]

    system._process_sabotage(balls4, 0)
    assert b4.crowd_sabotage_timer == 0
    assert b4.speed == 200.0
    assert not hasattr(b4, "crowd_sabotage_speed_active")
