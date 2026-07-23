import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []
        self.next_id = 9000

    def add_event(self, event_name, data):
        self.events.append([event_name, data])

class MockBall:
    def __init__(self):
        self.alive = True

def test_fake_bounties_mutator():
    mutator = GAME_MODES["fake_bounties_mutator"]
    world = MockWorld()
    balls = []

    # Fast forward to trigger spawn
    mutator.tick(world, balls, delta=15.0)

    # Verify a fake bounty was spawned
    assert len(world.balls) == 1
    fake_bounty = world.balls[0]
    assert getattr(fake_bounty, "is_fake_bounty", False)
    assert getattr(fake_bounty, "is_bounty", False)

    # Verify ping event emitted
    ping_events = [e for e in world.events if e[0] == "bounty_compass"]
    assert len(ping_events) == 1

    # Now destroy the fake bounty
    fake_bounty.alive = False

    # We need to pass the fake bounty as part of the balls array so it can be processed by tick
    balls.append(fake_bounty)

    mutator.tick(world, balls, delta=0.5)

    # Verify it was removed from world.balls
    assert len(world.balls) == 0

    # Verify a hazard was created
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "acid_puddle"

    # Verify explosion event was emitted
    explosion_events = [e for e in world.events if e[0] == "explosion"]
    assert len(explosion_events) == 1
    assert explosion_events[0][1]["radius"] == 100.0
