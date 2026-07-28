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
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "players"

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_squad_relay_mode():
    mode = GAME_MODES["squad_relay"]
    world = MockWorld()

    b1 = MockBall(1, 10, 10)
    b2 = MockBall(2, 20, 20)
    b3 = MockBall(3, 30, 30)
    balls = [b1, b2, b3]

    # We set their teams to be the same so they form a squad
    for b in balls:
        b.team = "team_A"

    mode.setup(world, balls)

    # Check that one is active and the others are spectators
    active = [b for b in balls if b.ball_type != "spectator"]
    spectators = [b for b in balls if b.ball_type == "spectator"]

    assert len(active) == 1
    assert len(spectators) == 2

    active_b = active[0]
    spectator_b = spectators[0]

    assert spectator_b.x == -1000.0

    # Kill the active ball
    active_b.hp = 0.0
    active_b.vx = 50.0
    active_b.vy = 25.0

    mode.tick(world, balls, 0.1)

    # The active ball should now be completely dead or spectator
    assert active_b.alive == False

    # One of the spectators should spawn in
    new_active = [b for b in balls if b.ball_type != "spectator" and b.alive]
    assert len(new_active) == 1

    spawned_b = new_active[0]

    # Should inherit speed
    assert spawned_b.vx == 50.0
    assert spawned_b.vy == 25.0
    assert spawned_b.x == active_b.x
    assert spawned_b.y == active_b.y

    # Should have invulnerability
    assert getattr(spawned_b, "intangible", False) == True
    assert getattr(spawned_b, "intangible_timer", 0.0) > 0.0


    # Tick again to make sure it doesn't chain reaction since the active is alive
    spawned_b.hp = 100.0
    spawned_b.alive = True

    mode.tick(world, balls, 0.1)

    # Active should still be 1
    new_active2 = [b for b in balls if b.ball_type != "spectator" and b.alive]
    assert len(new_active2) == 1
    assert new_active2[0].id == spawned_b.id
