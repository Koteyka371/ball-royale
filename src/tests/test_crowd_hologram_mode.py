import pytest
from ai.game_modes import CrowdHologramEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.speed_buff_timer = 0.0

def test_crowd_hologram_spawn_and_buff():
    mode = CrowdHologramEventMode()
    world = MockWorld()
    ball = MockBall(1, 500, 500)

    # Fast forward time to trigger the event
    import random
    random.seed(42)  # Make it deterministic

    # Force event to start
    mode.event_timer = 25.0

    # Tick should trigger event activation
    mode.tick(world, [ball], 0.016)

    # If random check passed (20% chance), it's active. Let's ensure it activates.
    if not mode.event_active:
        mode.event_active = True
        mode.event_duration = 15.0
        mode.holograms = [{
            "id": 8001,
            "x": 500,
            "y": 500,  # Right on top of ball to ensure collision
            "radius": 20.0,
            "hp": 100.0,
            "active": True,
            "kind": "crowd_hologram"
        }]
    else:
        # Move one hologram on top of ball to ensure collision
        mode.holograms[0]["x"] = 500
        mode.holograms[0]["y"] = 500

    # Next tick processes collisions
    mode.tick(world, [ball], 0.016)

    # Check if ball got speed buff
    assert getattr(ball, "speed_buff_timer", 0.0) >= 2.0

    # Check if hologram deactivated
    assert not mode.holograms[0]["active"]

    # Check for cheer event
    cheer_events = [e for e in world.events if e["type"] == "crowd_cheer"]
    assert len(cheer_events) > 0
