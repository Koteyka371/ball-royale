import pytest
from ai.acoustic_disruption_field import AcousticDisruptionFieldMode

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 10.0

class MockBall:
    def __init__(self, x, y, radius=10.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_acoustic_disruption_field_hazard_spawn():
    world = MockWorld()
    mode = AcousticDisruptionFieldMode()
    mode.event_timer = 15.0  # Trigger spawn

    mode.tick(world, [], 0.016)

    assert len(world.arena.hazards) == 1
    h = world.arena.hazards[0]
    assert getattr(h, "kind") == "acoustic_disruption"

def test_acoustic_disruption_field_blindness():
    world = MockWorld()
    mode = AcousticDisruptionFieldMode()

    ball = MockBall(100, 100)
    world.arena.hazards.append(MockHazard(1, 100, 100, 100.0, "acoustic_disruption"))

    mode.tick(world, [ball], 0.016)

    # Ball inside hazard should be blinded
    assert getattr(ball, "is_acoustically_blinded", False) == True
    assert getattr(ball, "perception_radius") == 0.0
    assert getattr(ball, "base_perception_radius_acoustic") == 250.0
    assert getattr(ball, "acoustic_blind_timer", 0.0) > 0.0

def test_acoustic_disruption_field_timer_restore():
    world = MockWorld()
    mode = AcousticDisruptionFieldMode()

    ball = MockBall(500, 500) # Outside the hazard range
    ball.is_acoustically_blinded = True
    ball.perception_radius = 0.0
    ball.base_perception_radius_acoustic = 250.0
    ball.acoustic_blind_timer = 0.1

    # Setup hazard far away
    world.arena.hazards.append(MockHazard(1, 100, 100, 100.0, "acoustic_disruption"))

    mode.tick(world, [ball], 0.2) # Tick enough to expire the timer

    # Timer should expire, restoring perception
    assert getattr(ball, "is_acoustically_blinded", False) == False
    assert getattr(ball, "perception_radius") == 250.0
    assert not hasattr(ball, "base_perception_radius_acoustic")
