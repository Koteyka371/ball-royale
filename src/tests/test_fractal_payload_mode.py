import pytest
from ai.game_modes import GAME_MODES, FractalPayloadMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.name = "Test Arena"

    def clamp_position(self, x, y, radius):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

    def get_nearby_entities(self, entity, radius):
        return []

class MockBall:
    def __init__(self, x=500, y=500):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "Red"
        self.radius = 10.0
        self.hologram_clones = []

def test_fractal_payload_mode():
    try:
        world = MockWorld()
        balls = [MockBall(300, 500), MockBall(700, 500)]
        mode = GAME_MODES["fractal_payload"]

        # Test Setup
        mode.setup(world, balls)
        assert len(mode.payloads) == 1

        initial_payload = mode.payloads[0]
        assert getattr(initial_payload, "depth", -1) == 0
        assert initial_payload.x == 500
        assert initial_payload.y == 500

        # Test Pushing mechanics
        initial_payload.x = 500
        balls[0].x = 450
        balls[0].y = 500

        mode.tick(world, balls, delta=0.1)
        # Red ball (at 450) is within push_radius (150) of payload (at 500).
        # Red pushes payload right (towards Blue goal, increasing x)
        assert initial_payload.x > 500

        # Test Detonation and Split
        # Force a detonation by setting timer to 0
        initial_payload.timer = 0

        balls_count_before = len(balls)
        mode.tick(world, balls, delta=0.1)

        # Payload should be dead
        assert initial_payload.alive == False

        alive_payloads = [p for p in mode.payloads if p.alive]
        assert len(alive_payloads) == 4

        for p in alive_payloads:
            assert p.depth == 1
            # max_hp is 10000 / (2**(depth+1)) = 10000 / 2 = 5000
            assert p.max_hp == 5000.0

        # Verify an event was added
        has_explosion = False
        for e in world.events:
            if e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "massive_explosion":
                has_explosion = True

        assert has_explosion

    finally:
        pass
