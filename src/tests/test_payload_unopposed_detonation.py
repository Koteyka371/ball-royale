import pytest
from ai.game_modes import EscortMode
from unittest.mock import Mock

class MockBall:
    def __init__(self, team="Defenders", x=100.0, y=500.0, alive=True):
        self.team = team
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = "player"
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 15.0
        self.vx = 0.0
        self.vy = 0.0
        self.id = id(self)

def test_payload_unopposed_timer_increases():
    mode = EscortMode()
    payload = MockBall(team="Defenders", x=100.0, y=500.0)
    payload.is_payload = True
    payload.ball_type = "payload"
    payload.speed = 0.5
    mode.payload = payload

    # Defender is near, attacker is far
    defender1 = MockBall(team="Defenders", x=120.0, y=500.0) # dist 20
    attacker1 = MockBall(team="Attackers", x=500.0, y=100.0) # dist > 150

    balls = [payload, defender1, attacker1]
    world = Mock()
    world.arena = Mock()
    world.arena.hazards = []
    world.add_event = Mock()

    mode.tick(world, balls, 1.0)

    assert getattr(payload, "unopposed_timer", 0.0) == 1.0

def test_payload_unopposed_timer_resets():
    mode = EscortMode()
    payload = MockBall(team="Defenders", x=100.0, y=500.0)
    payload.is_payload = True
    payload.ball_type = "payload"
    payload.speed = 0.5
    mode.payload = payload

    # Both are near
    defender1 = MockBall(team="Defenders", x=120.0, y=500.0) # dist 20
    attacker1 = MockBall(team="Attackers", x=130.0, y=500.0) # dist 30

    balls = [payload, defender1, attacker1]
    world = Mock()
    world.arena = Mock()
    world.arena.hazards = []
    world.add_event = Mock()

    payload.unopposed_timer = 5.0
    mode.tick(world, balls, 1.0)

    assert getattr(payload, "unopposed_timer", 0.0) == 0.0

def test_payload_unopposed_detonation():
    mode = EscortMode()
    payload = MockBall(team="Defenders", x=100.0, y=500.0)
    payload.is_payload = True
    payload.ball_type = "payload"
    payload.speed = 0.5
    mode.payload = payload

    defender1 = MockBall(team="Defenders", x=120.0, y=500.0) # dist 20
    attacker1 = MockBall(team="Attackers", x=500.0, y=100.0) # dist > 150

    balls = [payload, defender1, attacker1]
    world = Mock()
    world.arena = Mock()
    world.arena.hazards = []
    world.add_event = Mock()

    payload.unopposed_timer = 9.5
    mode.tick(world, balls, 1.0)

    # Should detonate
    assert getattr(payload, "unopposed_timer", 0.0) == 0.0

    # Check event
    found_event = False
    for call in world.add_event.call_args_list:
        if call[0][0] == "payload_unopposed_detonation":
            found_event = True
            break
    assert found_event, "Detonation event not emitted"

    # Check knockback (defender should be pushed)
    assert defender1.vx != 0.0 or defender1.vy != 0.0, "Defender was not knocked back"
