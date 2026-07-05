import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "players"
        self.tag_team_id = None
        self.tag_original_ball_type = None
        self.tag_original_team = None

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_tag_team_mode():
    mode = GAME_MODES["tag_team"]
    assert mode.name == "Tag Team"

    world = MockWorld()
    b1 = MockBall(1, 10.0, 10.0)
    b2 = MockBall(2, 20.0, 20.0)
    b3 = MockBall(3, 30.0, 30.0)
    b4 = MockBall(4, 40.0, 40.0)
    b5 = MockBall(5, 50.0, 50.0)
    b5.ball_type = "spectator" # should be ignored

    balls = [b1, b2, b3, b4, b5]
    mode.setup(world, balls)

    # Check teams were assigned properly
    teams = {}
    for b in balls:
        if b.ball_type == "spectator" and b.id == 5:
            assert b.tag_team_id is None
            continue

        tid = getattr(b, "tag_team_id", None)
        assert tid is not None
        if tid not in teams:
            teams[tid] = []
        teams[tid].append(b)

    assert len(teams) == 2 # 4 active balls -> 2 teams
    for tid, members in teams.items():
        assert len(members) == 2
        # One should be spectator
        b_types = [m.ball_type for m in members]
        assert "spectator" in b_types
        assert "player" in b_types

        for m in members:
            assert m.tag_original_ball_type == "player"
            assert m.tag_original_team == "players"
            if m.ball_type == "spectator":
                assert m.x == -1000.0
                assert m.y == -1000.0

    # Get one of the teams to test swapping
    tid = list(teams.keys())[0]
    m1, m2 = teams[tid]

    # Find who is active
    if m1.ball_type == "spectator":
        inactive = m1
        active = m2
    else:
        inactive = m2
        active = m1

    active.x = 100.0
    active.y = 200.0
    active.vx = 5.0
    active.vy = 10.0

    # Tick for 9.9 seconds - should not swap
    mode.tick(world, balls, delta=9.9)
    assert active.ball_type == "player"
    assert inactive.ball_type == "spectator"

    # Tick for another 0.2 seconds - should trigger swap
    mode.tick(world, balls, delta=0.2)

    # Now they should be swapped
    assert active.ball_type == "spectator"
    assert inactive.ball_type == "player"

    # Positions and velocities should be transferred
    assert inactive.x == 100.0
    assert inactive.y == 200.0
    assert inactive.vx == 5.0
    assert inactive.vy == 10.0

    assert active.x == -1000.0
    assert active.y == -1000.0

    assert len(world.events) > 0
