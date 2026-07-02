import pytest
import random
from arena.interactive_crowd_hazards import InteractiveCrowdHazards
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

def test_interactive_crowd_hazards_low_boredom():
    world = MockWorld()
    balls = [MockBall(1, "A", 100, 100)]

    random.seed(42)  # For reproducibility

    # Excitement is 15 (Boredom 5)
    excitement = 15.0

    # Run multiple times to ensure we hit the ~5% chance at least once
    hit = False
    for i in range(100):
        new_excitement = InteractiveCrowdHazards.process_boredom(excitement, balls, world)
        if new_excitement > excitement:
            hit = True
            break

    assert hit
    assert any(e[0] == "spawn_hazard" for e in world.events)
    assert any(e[0] == "crowd_throw" and "throws a hazard" in e[1]["message"] for e in world.events)

def test_interactive_crowd_hazards_high_boredom():
    world = MockWorld()
    balls = [MockBall(1, "A", 100, 100)]

    random.seed(42)

    # Excitement is 0 (Boredom 20) -> ~20% chance, 3 hazards
    excitement = 0.0

    hit = False
    for i in range(100):
        new_excitement = InteractiveCrowdHazards.process_boredom(excitement, balls, world)
        if new_excitement > excitement:
            hit = True
            break

    assert hit
    spawn_events = [e for e in world.events if e[0] == "spawn_hazard"]
    assert len(spawn_events) == 3
    assert any(e[0] == "crowd_throw" and "throws hazards" in e[1]["message"] for e in world.events)

def test_interactive_crowd_hazards_no_balls():
    world = MockWorld()
    balls = [MockBall(1, "A", 0, 100, alive=False)]

    excitement = 0.0
    new_excitement = InteractiveCrowdHazards.process_boredom(excitement, balls, world)

    assert new_excitement == excitement
    assert len(world.events) == 0

def test_interactive_crowd_hazards_high_excitement():
    world = MockWorld()
    balls = [MockBall(1, "A", 100, 100)]

    excitement = 50.0
    new_excitement = InteractiveCrowdHazards.process_boredom(excitement, balls, world)

    assert new_excitement == excitement
    assert len(world.events) == 0
