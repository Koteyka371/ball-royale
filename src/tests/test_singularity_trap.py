import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind, x, y, radius, duration):
        self.id = 12345
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration

class MockBall:
    def __init__(self, id, x, y, team="blue", ball_type="brawler"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.hp = 100
        self.alive = True
        self.base_speed = 10.0
        self.speed = 10.0
        self.radiation_multiplier = 1.0

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards else []

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls if balls else []
        self.arena = arena if arena else MockArena()
        self.events = []

def test_singularity_trap_pull_and_slow():
    # Setup
    trap = MockHazard("singularity_trap", 100.0, 100.0, 150.0, 5.0)
    target = MockBall(1, 150.0, 100.0) # 50 units away

    world = MockWorld(balls=[target], arena=MockArena([trap]))
    action = Action(target, world)

    # Execute action to process hazards
    # Note: action._process_hazards is called inside execute
    # Actually action._process_hazards is not a separate method, it's inside `execute`.
    # We can just call execute("idle", 0.1)

    initial_x = target.x
    initial_hp = target.hp

    action.execute("idle", 0.1)

    # Assert duration decreased
    assert trap.duration == 4.9

    # Assert pull (target should move closer to trap)
    assert target.x < initial_x

    # Assert slow down
    assert target.speed == target.base_speed * 0.5

    # Assert increasing collision damage mechanism (radiation multiplier)
    assert target.radiation_multiplier > 1.0

    # Assert damage over time
    assert target.hp < initial_hp

def test_singularity_trap_explosion():
    # Setup trap to explode this tick
    trap = MockHazard("singularity_trap", 100.0, 100.0, 150.0, 0.1)

    # Ball inside radius
    target_in = MockBall(1, 150.0, 100.0)
    # Ball outside radius
    target_out = MockBall(2, 300.0, 100.0)

    world = MockWorld(balls=[target_in, target_out], arena=MockArena([trap]))
    action = Action(target_in, world)

    # Expected: trap duration -> 0.0 -> explodes -> deals 50 damage -> removed
    action.execute("idle", 0.1)

    assert trap.duration == 0.0
    assert getattr(trap, 'marked_for_removal', False) == True

    # Target in radius takes explosion damage (+ DOT from the last tick)
    assert target_in.hp <= 50.0 # 100 - 50 (explosion) - DOT

    # Target outside radius takes NO explosion damage and NO DOT
    assert target_out.hp == 100.0

    # Explosion event created
    assert len(world.events) == 1
    assert world.events[0]["type"] == "explosion"
