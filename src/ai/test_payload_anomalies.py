from .game_modes import GAME_MODES, GameMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, ball_type, is_payload=False):
        self.id = id
        self.ball_type = ball_type
        self.is_payload = is_payload
        self.alive = True
        self.team = "Red"
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0

def test_payload_anomalies_spawn_and_effects():
    world = MockWorld()
    mode = GameMode()

    payload = MockBall(1, "payload", is_payload=True)
    player = MockBall(2, "player")
    player.x = 450.0
    player.y = 500.0

    balls = [payload, player]

    # 1. Timer should start at 15 and decrement
    mode.apply_dynamic_traits(world, balls, 1.0)
    assert world.payload_anomaly_timer == 14.0

    # Force timer to 0 to trigger spawn
    world.payload_anomaly_timer = 0.0
    import random
    random.seed(42) # Try to predict if it's well or conveyor, but we'll check both

    mode.apply_dynamic_traits(world, balls, 0.016)

    assert world.payload_anomaly_timer > 0 # Reset to 20.0

    # Either a gravity well spawned (in balls) or a conveyor spawned (in hazards)
    has_well = any(getattr(b, "ball_type", "") == "gravity_well" for b in balls)
    has_conveyor = any(getattr(h, "kind", "") == "payload_conveyor" for h in world.arena.hazards)

    assert has_well or has_conveyor

    if has_well:
        well = next(b for b in balls if getattr(b, "ball_type", "") == "gravity_well")
        # Player should be pulled towards well
        # We need to manually set positions to test effect
        well.x = 800.0
        well.y = 500.0
        player.x = 500.0
        player.y = 500.0
        player.vx = 0.0

        mode.apply_dynamic_traits(world, balls, 0.5)
        # well is at 800, player at 500. Player should be pulled right (positive vx)
        assert player.vx > 0

        # Test destruction
        well.hp = 0
        mode.apply_dynamic_traits(world, balls, 0.016)
        assert not well.alive

    if has_conveyor:
        # Check conveyor effect
        world.arena.hazards = [{
            "kind": "payload_conveyor",
            "x": 500.0,
            "y": 500.0,
            "radius": 250.0,
            "dir_x": 1.0,
            "dir_y": 0.0,
            "timer": 15.0
        }]

        player.x = 500.0
        player.y = 500.0
        player.vx = 0.0
        payload.x = 500.0
        payload.y = 500.0

        mode.apply_dynamic_traits(world, balls, 0.5)

        # Payload gets directly pushed (x increases)
        assert payload.x > 500.0
        # Player gets vx applied
        assert player.vx > 0.0
