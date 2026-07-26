import pytest
from ai.double_juggernaut import DoubleJuggernautMode

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append({"type": event_type, "data": event_data})

class MockBall:
    def __init__(self, ball_id, ball_type="normal"):
        self.id = ball_id
        self.ball_type = ball_type
        self.alive = True
        self.team = "unknown"
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_max_hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.radius = 10.0
        self.base_radius = 10.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.mass = 1.0
        self.base_mass = 1.0
        self.x = 50.0
        self.y = 50.0

def test_setup_assigns_juggernauts():
    mode = DoubleJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4)]

    mode.setup(world, balls)

    assert balls[0].team == "Juggernaut"
    assert balls[1].team == "Juggernaut"
    assert balls[2].team == "Hunters"
    assert balls[3].team == "Hunters"

    # Verify stat boosts for juggernauts
    assert balls[0].max_hp == 500.0
    assert balls[0].hp == 500.0
    assert balls[0].damage > 10.0
    assert balls[0].radius == 20.0
    assert balls[0].speed < 100.0
    assert balls[0].mass == 3.0

    # Verify stats for hunters
    assert balls[2].max_hp == 80.0

def test_tick_spawns_heal_and_enrages():
    mode = DoubleJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)

    # Kill the first juggernaut
    balls[0].alive = False

    mode.tick(world, balls, 0.016)

    # Verify heal dropped
    assert any(b["type"] == "massive_heal" for b in world.boosters)
    assert getattr(balls[0], "dropped_heal", False) is True

    # Verify second juggernaut enraged
    assert getattr(balls[1], "enraged", False) is True
    assert balls[1].damage > 15.0
    assert balls[1].speed > 100.0
    assert balls[1].radius == 25.0

    # Verify events
    event_types = [e["type"] for e in world.events]
    assert "juggernaut_death" in event_types
    assert "juggernaut_enrage" in event_types

def test_win_conditions():
    mode = DoubleJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    # Kill hunters
    balls[2].alive = False
    assert mode.check_winner(world, balls) == "Juggernaut"

    # Bring hunters back, kill juggernauts
    balls[2].alive = True
    balls[0].alive = False
    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Hunters"

    # Kill everyone
    balls[2].alive = False
    assert mode.check_winner(world, balls) == "Draw"
